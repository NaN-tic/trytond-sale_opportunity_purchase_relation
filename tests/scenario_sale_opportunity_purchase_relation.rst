===========================================
Sale Opportunity Purchase Relation Scenario
===========================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install sale::

    >>> Module = Model.get('ir.module.module')
    >>> sale_module, = Module.find(
    ...     [('name', '=', 'sale_opportunity_purchase_relation')])
    >>> Module.install([sale_module.id], config.context)
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='U.S. Dollar', symbol='$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
    ...         mon_decimal_point='.', mon_thousands_sep=',')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find([])

Reload the context::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> FiscalYear = Model.get('account.fiscalyear')
    >>> Sequence = Model.get('ir.sequence')
    >>> SequenceStrict = Model.get('ir.sequence.strict')
    >>> fiscalyear = FiscalYear(name=str(today.year))
    >>> fiscalyear.start_date = today + relativedelta(month=1, day=1)
    >>> fiscalyear.end_date = today + relativedelta(month=12, day=31)
    >>> fiscalyear.company = company
    >>> post_move_seq = Sequence(name=str(today.year), code='account.move',
    ...     company=company)
    >>> post_move_seq.save()
    >>> fiscalyear.post_move_sequence = post_move_seq
    >>> invoice_seq = SequenceStrict(name=str(today.year),
    ...     code='account.invoice', company=company)
    >>> invoice_seq.save()
    >>> fiscalyear.out_invoice_sequence = invoice_seq
    >>> fiscalyear.in_invoice_sequence = invoice_seq
    >>> fiscalyear.out_credit_note_sequence = invoice_seq
    >>> fiscalyear.in_credit_note_sequence = invoice_seq
    >>> fiscalyear.save()
    >>> FiscalYear.create_period([fiscalyear.id], config.context)

Create chart of accounts::

    >>> AccountTemplate = Model.get('account.account.template')
    >>> Account = Model.get('account.account')
    >>> Journal = Model.get('account.journal')
    >>> account_template, = AccountTemplate.find([('parent', '=', None)])
    >>> create_chart = Wizard('account.create_chart')
    >>> create_chart.execute('account')
    >>> create_chart.form.account_template = account_template
    >>> create_chart.form.company = company
    >>> create_chart.execute('create_account')
    >>> receivable, = Account.find([
    ...         ('kind', '=', 'receivable'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> payable, = Account.find([
    ...         ('kind', '=', 'payable'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> revenue, = Account.find([
    ...         ('kind', '=', 'revenue'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> expense, = Account.find([
    ...         ('kind', '=', 'expense'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> create_chart.form.account_receivable = receivable
    >>> create_chart.form.account_payable = payable
    >>> create_chart.execute('create_properties')
    >>> cash, = Account.find([
    ...         ('kind', '=', 'other'),
    ...         ('name', '=', 'Main Cash'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> cash_journal, = Journal.find([('type', '=', 'cash')])
    >>> cash_journal.credit_account = cash
    >>> cash_journal.debit_account = cash
    >>> cash_journal.save()

Create Employee::

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

    >>> PaymentTerm = Model.get('account.invoice.payment_term')
    >>> PaymentTermLine = Model.get('account.invoice.payment_term.line')
    >>> payment_term = PaymentTerm(name='Direct')
    >>> payment_term_line = PaymentTermLine(type='remainder', days=0)
    >>> payment_term.lines.append(payment_term_line)
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

    >>> convert_wizard_id = opportunity.click('convert')
    >>> IrWizard = Model.get('ir.action.wizard')
    >>> wizard = IrWizard(convert_wizard_id)
    >>> convert_wizard = Wizard(wizard.wiz_name, models=[opportunity])
    >>> Sale = Model.get('sale.sale')
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
