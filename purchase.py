#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['Purchase', 'PurchaseLine']
__metaclass__ = PoolMeta


class Purchase:
    __name__ = 'purchase.purchase'

    sales = fields.Function(fields.One2Many('sale.sale', None,
            'Sales'), 'get_sales')
    opportunities = fields.Function(fields.One2Many('sale.opportunity', None,
            'Sales'), 'get_opportunities')

    def get_sales(self, name):
        pool = Pool()
        Line = pool.get('sale.line')
        lines = Line.search([
                ('purchase_lines', 'in', [x.id for x in self.lines]),
                ])
        return list(set([l.sale.id for l in lines]))

    def get_opportunities(self, name):
        pool = Pool()
        Line = pool.get('sale.opportunity.line')
        lines = Line.search([
                ('purchase_lines', 'in', [x.id for x in self.lines]),
                ])
        return list(set([l.opportunity.id for l in lines]))


class PurchaseLine:
    __name__ = 'purchase.line'

    sale_lines = fields.Many2Many('sale.line-purchase.line',
        'purchase_line', 'sale_line', 'Sale Lines',
        domain=[
            ('product', '=', Eval('product', 0)),
            ],
        depends=['product'])

    opportunity_lines = fields.Many2Many('sale.opportunity.line-purchase.line',
        'purchase_line', 'opportunity_line', 'Opportunity Lines',
        domain=[
            ('product', '=', Eval('product', 0)),
            ],
        depends=['product'])
