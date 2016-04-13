# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

__all__ = ['Sale', 'SaleLinePurchaseLine', 'SaleLine']


class Sale:
    __name__ = 'sale.sale'
    __metaclass__ = PoolMeta

    purchases = fields.Function(fields.One2Many('purchase.purchase', None,
            'Purchases'), 'get_purchases', searcher='search_purchases')

    def get_purchases(self, name):
        return list(set([pl.purchase.id for l in self.lines
                    for pl in l.purchase_lines]))

    @classmethod
    def search_purchases(cls, name, clause):
        return [('lines.purchase_lines.purchase.id',) + tuple(clause[1:])]


class SaleLinePurchaseLine(ModelSQL):
    'Sale Line - Purchase Line'
    __name__ = 'sale.line-purchase.line'
    purchase_line = fields.Many2One('purchase.line', 'Purchase Line',
        required=True, select=True, ondelete='CASCADE')
    sale_line = fields.Many2One('sale.line', 'Sale Line',
        required=True, select=True, ondelete='CASCADE')


class SaleLine:
    __name__ = 'sale.line'
    __metaclass__ = PoolMeta

    purchase_lines = fields.Many2Many('sale.line-purchase.line',
        'sale_line', 'purchase_line', 'Purchase Lines', readonly=True,
        domain=[
            ('product', '=', Eval('product', 0)),
            ],
        depends=['product'])
