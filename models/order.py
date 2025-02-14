# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class OrderManagement(models.Model):
    _name = 'order_management.order_management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Gestion des Commandes'

    # Identification de la commande
    name = fields.Char(string="order reference",
                       required=True,
                       copy=False,
                       readonly=True,
                       default="New"
                       )

    # Informations sur le client
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)

    # État de la commande
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In progress'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='draft', required=True, track_visibility='onchange')

    # Dates importantes
    order_date = fields.Datetime(string="Order date", default=fields.Datetime.now, required=True)
    delivery_date = fields.Datetime(string="Delivery date")

    # Produits de la commande
    order_line_ids = fields.One2many('order_management.order_line', 'order_id', string="Order Lines")

    # Totaux financiers
    amount_untaxed = fields.Float(string="Montant Hors Taxes", compute="_compute_amount", store=True)
    amount_tax = fields.Float(string="Montant Taxes", compute="_compute_amount", store=True)
    amount_total = fields.Float(string="Montant Total TTC", compute="_compute_amount", store=True)

    # Notes et communication
    note = fields.Text(string="Remarques")

    # Métadonnées
    user_id = fields.Many2one('res.users',
                              string="Responsable",
                              domain=[('groups_id.name', '=', 'Team Sale')]
                              )
    current_user_id = fields.Many2one('res.users', string="Employé", default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)

    # Calcul des totaux
    @api.depends('order_line_ids.price_subtotal')
    def _compute_amount(self):
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line_ids)
            amount_tax = sum(line.price_tax for line in order.order_line_ids)
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('order_management.order_management') or 'New'
        order = super(OrderManagement, self).create(vals)
        # Créer un rappel pour le responsable
        order.create_reminder()
        return order

    def action_confirm_order(self):
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise AccessError(_("Seuls les chefs des ventes peuvent confirmer une commande."))
        self.state = 'confirmed'
        # Créer un rappel pour l'employé en charge de la commande
        self.create_employee_reminder()
        return True

    def action_deliver_order(self):
        self.state = 'delivered'

    def create_reminder(self):
        """Créer un rappel pour le responsable."""
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model'].search([('model', '=', 'order_management.order_management')], limit=1).id

        self.env['mail.activity'].create({
            'res_id': self.id,
            'res_model_id': model_id,
            'activity_type_id': activity_type_id,
            'summary': 'Order Management Reminder',
            'note': 'N\'oubliez pas de traiter cette commande.',
            'user_id': self.user_id.id,
            'date_deadline': fields.Date.today(),
        })

    def create_employee_reminder(self):
        """Créer un rappel pour l'employé en charge de la commande."""
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model'].search([('model', '=', 'order_management.order_management')], limit=1).id

        self.env['mail.activity'].create({
            'res_id': self.id,
            'res_model_id': model_id,
            'activity_type_id': activity_type_id,
            'summary': 'Rappel pour l\'employé en charge de la commande',
            'note': 'Veuillez traiter cette commande.',
            'user_id': self.current_user_id.id,
            'date_deadline': fields.Date.today(),
        })

class OrderLine(models.Model):
    _name = 'order_management.order_line'
    _description = 'Lignes de Commande'

    product_id = fields.Many2one('product.product', string="Produit", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    price_unit = fields.Float(string="Price Unit", related="product_id.list_price", readonly=True)
    price_subtotal = fields.Float(string="Subtotal", compute="_compute_price_subtotal", store=True)
    price_tax = fields.Float(string="Tax", compute="_compute_price_subtotal", store=True)

    order_id = fields.Many2one('order_management.order_management', string="Command", required=True)

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            line.price_tax = line.price_subtotal * 0.1925  # Exemple : 19.25 % de taxes
