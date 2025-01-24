# -*- coding: utf-8 -*-
# from odoo import http


# class OrderManagement(http.Controller):
#     @http.route('/order_management/order_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/order_management/order_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('order_management.listing', {
#             'root': '/order_management/order_management',
#             'objects': http.request.env['order_management.order_management'].search([]),
#         })

#     @http.route('/order_management/order_management/objects/<model("order_management.order_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('order_management.object', {
#             'object': obj
#         })

