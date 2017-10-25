===========================================
Sale Opportunity Purchase Relation Scenario
===========================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard, Report
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install sale::

    >>> Module = Model.get('ir.module')
    >>> sale_module, = Module.find(
    ...     [('name', '=', 'sale_opportunity_purchase_relation')])
    >>> Module.install([sale_module.id], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()


Reload the context::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

    >>> Journal = Model.get('account.journal')
    >>> cash_journal, = Journal.find([('type', '=', 'cash')])
    >>> cash_journal.credit_account = cash
    >>> cash_journal.debit_account = cash
    >>> cash_journal.save()

Create Employee::

    >>> Party = Model.get('party.party')
    >>> Employee = Model.get('company.employee')
    >>> party = Party(name='Employee')
    >>> party.save()
    >>> employee = Employee()
    >>> employee.party = party
    >>> employee.company = company
    >>> employee.save()
    >>> user, = User.find([])
    >>> user.employees.append(employee)
    >>> user.employee = employee
    >>> user.save()
    >>> config._context = User.get_preferences(True, config.context)

Create parties::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create category::

    >>> ProductCategory = Model.get('product.category')
    >>> category = ProductCategory(name='Category')
    >>> category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.category = category
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.purchasable = True
    >>> template.salable = True
    >>> template.list_price = Decimal('10')
    >>> template.cost_price = Decimal('5')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()


Create an Opportunity::

    >>> Opportunity = Model.get('sale.opportunity')
    >>> OpportunityLine = Model.get('sale.opportunity.line')
    >>> opportunity = Opportunity()
    >>> opportunity.party = customer
    >>> opportunity.payment_term = payment_term
    >>> opportunity.description = 'Opportunity'
    >>> opportunity_line = opportunity.lines.new()
    >>> opportunity_line.product = product
    >>> opportunity_line.quantity = 10
    >>> opportunity.save()
    >>> opportunity.click('opportunity')
    >>> opportunity_line, = opportunity.lines
    >>> opportunity_line = OpportunityLine(opportunity_line.id)

Create a purchase to fill the opportunity and relate them::

    >>> Purchase = Model.get('purchase.purchase')
    >>> purchase = Purchase()
    >>> purchase.party = supplier
    >>> purchase.payment_term = payment_term
    >>> purchase_line = purchase.lines.new()
    >>> purchase_line.product = product
    >>> purchase_line.quantity = 10
    >>> purchase_line.opportunity_lines.append(opportunity_line)
    >>> purchase.click('quote')
    >>> purchase_line, = purchase.lines
    >>> opportunity.reload()
    >>> opportunity.purchases == [purchase]
    True

Convert the opportunity and check sale is related to the same purchase line::

    >>> opportunity.click('convert')
    >>> sale, = opportunity.sales
    >>> sale_line, = sale.lines
    >>> sale_line_purchase_line, = sale_line.purchase_lines
    >>> sale_line_purchase_line == purchase_line
    True
    >>> purchase.reload()
    >>> purchase.sales == [sale]
    True
    >>> purchase.opportunities == [opportunity]
    True

Create a new opportunity related to the same purchase line::

    >>> new_opportunity, = Opportunity.copy([opportunity.id], config.context)
    >>> new_opportunity = Opportunity(new_opportunity)
    >>> new_line, = opportunity.lines
    >>> new_line_purchase_line, = new_line.purchase_lines
    >>> new_line_purchase_line == purchase_line
    True

Mark the new opportunity as lost and check purchase is not cancelled::

    >>> new_opportunity.click('lost')
    >>> purchase.reload()
    >>> purchase.state
    u'quotation'

Mark the opportunity as lost and check that purchase is canceled::

    >>> opportunity.click('lost')
    >>> purchase.reload()
    >>> purchase.state
    u'cancel'
