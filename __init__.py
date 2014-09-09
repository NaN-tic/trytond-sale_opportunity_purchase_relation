# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .sale import *
from .opportunity import *
from .purchase import *


def register():
    Pool.register(
        Sale,
        SaleLinePurchaseLine,
        SaleLine,
        Opportunity,
        OpportunityLinePurchaseLine,
        OpportunityLine,
        Purchase,
        PurchaseLine,
        module='sale_opportunity_purchase_relation', type_='model')
