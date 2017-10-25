# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta

__all__ = ['Opportunity', 'OpportunityLinePurchaseLine', 'OpportunityLine']


class Opportunity:
    __name__ = 'sale.opportunity'
    __metaclass__ = PoolMeta

    purchases = fields.Function(fields.One2Many('purchase.purchase', None,
            'Purchases'), 'get_purchases', searcher='search_purchases')

    def get_purchases(self, name):
        return list(set([pl.purchase.id for l in self.lines
                    for pl in l.purchase_lines]))

    @classmethod
    def search_purchases(cls, name, clause):
        return [('lines.purchase_lines.purchase.id',) + tuple(clause[1:])]

    @classmethod
    def cancel_purchases(cls, opportunities):
        pool = Pool()
        Purchase = pool.get('purchase.purchase')
        to_cancel = []
        for opportunity in opportunities:
            for purchase in opportunity.purchases:
                if all(o.state in ('cancel', 'lost')
                        for o in purchase.opportunities):
                    to_cancel.append(purchase)
        if to_cancel:
            Purchase.cancel(to_cancel)

    @classmethod
    def lost(cls, opportunities):
        super(Opportunity, cls).lost(opportunities)
        cls.cancel_purchases(opportunities)

    @classmethod
    def cancel(cls, opportunities):
        super(Opportunity, cls).cancel(opportunities)
        cls.cancel_purchases(opportunities)


class OpportunityLinePurchaseLine(ModelSQL):
    'Opportunity Line - Purchase Line'
    __name__ = 'sale.opportunity.line-purchase.line'
    purchase_line = fields.Many2One('purchase.line', 'Purchase Line',
        required=True, select=True, ondelete='CASCADE')
    opportunity_line = fields.Many2One('sale.opportunity.line',
        'Opportunity Line', required=True, select=True, ondelete='CASCADE')


class OpportunityLine:
    __name__ = 'sale.opportunity.line'
    __metaclass__ = PoolMeta

    purchase_lines = fields.Many2Many('sale.opportunity.line-purchase.line',
        'opportunity_line', 'purchase_line', 'Purchase Lines', readonly=True,
        domain=[
            ('product', '=', Eval('product', 0)),
            ],
        depends=['product'])

    def get_sale_line(self, sale):
        line = super(OpportunityLine, self).get_sale_line(sale)
        line.purchase_lines = self.purchase_lines
        if not line.purchase_lines:
            for sale_line in self.sale_lines:
                if sale_line.purchase_lines:
                    line.purchase_lines = sale_line.purchase_lines
                    break
        return line

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['purchase_lines'] = None
        return super(OpportunityLine, cls).copy(lines, default=default)
