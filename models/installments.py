# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderInherit1(models.Model):
    _inherit = 'sale.order.line'
    size = fields.Selection([
        ('large', 'Large'),
        ('small', 'Small'),
        ('medium', 'Medium')], default='large', required=True, store=True)


class InheritStockLine(models.Model):
    _inherit = 'stock.move'
    size = fields.Selection([
        ('large', 'Large'),
        ('small', 'Small'),
        ('medium', 'Medium')], compute="get_size_value", required=True, string="Size", readonly=False, store=True)
    sale_line_id = fields.Many2one('sale.order.line', index=True)

    @api.depends('sale_line_id.size')
    def get_size_value(self):
        for rec in self:
            rec.size = rec.sale_line_id.size



class Installment(models.Model):
    _name = 'installment.installment'
    _description = "Odoo dev task"

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('installment.installment.sequence') or _('New')
        result = super(Installment, self).create(vals)
        return result

    def open_registration(self):
        for rec in self:
            rec.state = 'open'
            inv = self.env['account.move'].create({
                'type': 'out_invoice',
                'partner_id': self.customer.id})
            self.invoice_id = inv.id

    def open_invoice(self):
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_id.id,
        }

    def settlement_paid(self):
        self.write({'state': 'paid'})
        return {}

    invoice_id = fields.Many2one('account.move')
    color = fields.Integer()
    ref = fields.Char(string='INVOICE.ID', readonly=True,
                      default=lambda self: _('New'))

    amount = fields.Float(required=True, positive=True)
    name = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid')],
        string='Status', default='draft', readonly=True, copy=False, tracking=True)
    date = fields.Date(string="Date", default=fields.Date.today)
    customer = fields.Many2one('res.partner', string="Customer", required=True)
    journal = fields.Many2one('account.journal', string="Journal", required=True)
    account = fields.Many2one('account.account', string="Account", required=True)
    analytic_account = fields.Many2one('account.analytic.account', string="Analytic account")
    analytic_tags = fields.Many2many('res.partner', string="Analytic tags")
    note = fields.Text(string="Notes")
    reference = fields.Char("Reference")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    included_services = fields.Many2many('product.product', string="Products Here")


class ReviewButton(models.Model):
    _inherit = "account.move"
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('review', 'Reviewed'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    def action_review(self):
        self.state = 'review'
