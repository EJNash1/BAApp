from gluon import DAL
db2 = DAL('firebird://sysdba:aquafresh@10.122.18.18:3053/C:\\WSI\\Data\\LPIBEW134.FDB')
db = DAL('sqlite://storage1.db')

from gluon.tools import Auth
auth = Auth(db)

"""
gfd - 11/10/2013 12:30am - Manually creating Auth tables because Web2Py tries to create table without setting id to NOT NULL
"""

auth.next = None
auth.settings.login_next = URL('index')
auth.settings.actions_disabled=['register','change_password','request_reset_password','retrieve_username','profile']
auth.settings.login_email_validate = False

db.define_table('Files',
                Field('name', 'string', length=255),
                Field('phile', 'upload', uploadfolder=request.folder+'static/downloads', label='File', requires =  IS_UPLOAD_FILENAME(extension='pdf')),
                auth.signature)

db2.define_table('Employer',
    Field('EMPLOYER_CODE',),
    Field('EMPLOYER_NAME' ,),
    Field('OWNER',),
    Field('EIT_CODE'),
    Field('INACTIVE_RECORD' ,),
    primarykey=['EMPLOYER_CODE'],
    format='%(EMPLOYER_NAME)s',
    migrate=False)

db2.define_table('GAD_EMPLOYER_EXHIBIT_A',
                 Field('employerid',db2.Employer, label='Employer', requires=IS_EMPTY_OR(IS_IN_DB(db2, 'Employer.EMPLOYER_CODE','%(EMPLOYER_NAME)s'))),
                 Field('employername',readable=False, writable=False),
                 Field('jobclass',label='Job Class'),
                 Field('rate_year',label='Year'),
                 Field('rate_start',label='Start Rate'),
                 Field('rate_twelvemnth',label='12 Month Rate'),
                 Field('rate_twentyfourmnth',label='24 Month Rate'),
                 migrate=False)

db2.define_table('GAD_IP_JOURNAL',
                 Field('MEMBER_TABLE_ID'),
                 Field('FIRST_NAME'),
                 Field('MI'),
                 Field('LAST_NAME'),
                 Field('MEMBER_STATUS_CODE'),
                 migrate=False)

db2.define_table('WORK_PERMIT',
    Field('PERMIT_EXPIRATION_DATE',),
    Field('PORTABILITY_AGREEMENT_CODE' ,),
    Field('EMPLOYMENT_HISTORY_TABLE_ID',),
    Field('INACTIVE_RECORD' ,),
    migrate=False)

db2.define_table('EMPLOYMENT_HISTORY',
    Field('EMPLOYMENT_HISTORY_TABLE_ID',),
    Field('EMPLOYER_CODE' ,),
    Field('MEMBER_TABLE_ID',),
    migrate=False)

db2.define_table('QUALIFIED_BOOKS',
    Field('MEMBER_TABLE_ID',),
    Field('BOOK_NAME' ,),
    migrate=False)

db2.define_table('WebAppLog',
    Field('id', 'int'),
    Field('UserName', 'text'),
    Field('IPAddress',),
    migrate=False)
db2.define_table('Member_Payment_Date',
    Field('MEMBER_TABLE_ID', 'reference Member.MEMBER_TABLE_ID', represent=lambda id, r: findpaidthru(r.MEMBER_TABLE_ID)),
    Field('PAID_THRU_DATE' , 'text', represent = lambda PAID_THRU_DATE, row: PAID_THRU_DATE.strftime('%m/%Y')),
    Field('CHARGE_CODE' ,),
    primarykey=['MEMBER_TABLE_ID'],
    format='%(PAID_THRU_DATE)s',
    migrate=False)
db2.define_table('Member',
    Field('MEMBER_TABLE_ID' ,),
    Field('MEMBER_ID' ,),
    Field('FIRST_NAME' , 'text'),
    Field('MI', 'text'),
    Field('LAST_NAME' , 'text'),
    Field('LAST_NAME_MIXED' , 'text'),
    Field('CARD_NUMBER' , 'text'),
    Field('STATE' , 'text'),
    Field('ZIP' , 'text'),
    Field('BIRTHDATE' , 'datetime'),
    Field('JOB_CLASS_CODE' , 'text', label='Job Class'),
    Field('DUES_TYPE_CODE', readable=False, writable=False),
    Field('LOCAL_CODE' , ),
    Field('DUES_CHECKOFF' , represent= lambda id, r: SPAN(duecheck(r.Member.DUES_CHECKOFF),_style='color:red' if r.Member.DUES_CHECKOFF=='F' else 'color:green')),
    Field('MEMBER_STATUS_CODE' , 'text'),
    Field('EMPLOYER_CODE' , 'reference Employer.EMPLOYER_CODE', represent=lambda id, r: findempname(r.EMPLOYER_CODE)),
    primarykey=['MEMBER_TABLE_ID'],
    migrate=False)

#db2.Member_Payment_Date.PAID_THRU_DATE.represent = lambda r:v.strftime('%m-%d-%Y')
db2.define_table('MEMBER_TRANSACTION',
    Field('MEMBER_TABLE_ID'),
    Field('TRANSACTION_DATE'),
    primarykey=['MEMBER_TABLE_ID'],
    migrate=False)

db2.define_table('EIT_DEDUCTION',
    Field('WORK_DATE'),
    Field('GROSS_WAGES', 'float'),
    Field('DEDUCTION_AMOUNT', 'float'),
    Field('MEMBER_TABLE_ID'),
    primarykey=['MEMBER_TABLE_ID'],
    migrate=False)


def get_header_labels(table=None):
    headers = {}
    for field in db2[table].fields:
        headers[table+'.'+field] = db2[table][field].label
    return headers

db2.Member.EMPLOYER_CODE.requires=IS_IN_DB(db2,db2.Employer.EMPLOYER_CODE,'Employer.EMPLOYER_NAME')
db2.Member_Payment_Date.PAID_THRU_DATE.requires=IS_IN_DB(db2,db2.Member_Payment_Date.PAID_THRU_DATE,'Member_Payment_Date.MEMBER_TABLE_ID')

def duecheck(record):
    answer = None
    if record == 'F':
        answer = 'Has not signed yet.'
    elif record == 'T':
        answer = 'Has signed.'
    return '%s' % (answer)

def findempname(record):
    Noemp = 'None'
    if record is None:
        return '%s' % (Noemp)
    rows = db2(db2.Employer.EMPLOYER_CODE==record).select()
    last_row = rows.last()
    if last_row is None:
         return '%s' % (Noemp)
    return '%s' % (last_row.EMPLOYER_NAME)

def findpaidthru(record):
    amount = db2(db2.Member_Payment_Date.MEMBER_TABLE_ID==record).count()
    person = db2(db2.Member.MEMBER_TABLE_ID==record).select()
    lr = person.last()
    person2 = str(lr.LOCAL_CODE)
    date22 = None
    if person2 == '0134':
        rows =  db2((db2.Member_Payment_Date.MEMBER_TABLE_ID==record) & (db2.Member_Payment_Date.CHARGE_CODE=='D')).select()
        last_row = rows.first()
        if last_row is not None:
            date2 = str(last_row.PAID_THRU_DATE)
            date22 = date2[:10]
    else:
        rows =  db2((db2.Member_Payment_Date.MEMBER_TABLE_ID==record) & (db2.Member_Payment_Date.CHARGE_CODE=='W')).select()
        last_row = rows.last()
        if last_row is not None:
            date2 = str(last_row.PAID_THRU_DATE)
            date22 = date2[:10]
    return '%s' % (date22)

from gluon.tools import Crud, Service, PluginManager, prettydate


from gluon.contrib.login_methods.ldap_auth import ldap_auth
auth.settings.login_methods = [ldap_auth(mode='ad',
  server='L134-SRV01',
  base_dn='ou="Union Hall",dc=local134,dc=org')]

auth.define_tables(username=True)




# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Main controller for UnionHall WebApp
## -
## -
## -
##
#########################################################################
import Crypto.Cipher
from pyDes import *
from datetime import date

@auth.requires_login()
def documents():
    db.Files.id.readable=False
    db.Files.phile.readable=False
    form=SQLFORM(db.Files, formstyle='bootstrap')
    form.elements('input.string', replace=lambda el: el.add_class('form-control'))
    form.elements('input.btn', replace=lambda el: el.add_class('btn-primary'))
    if form.process().accepted:
        response.flash = "files updated"
    links=[lambda row: A('View Document!', _href=URL('default', 'documents', args=['download/'+str(row.phile)]), _class='two btn btn-success btn-lg')]
    form2=SQLFORM.grid(db.Files, links=links, maxtextlength=200, details=False, searchable=False, editable=False, csv=False, create=False, deletable=False, user_signature=False, buttons_placement='left')
    form2.element('th', replace=TH(' ', _class='xyz', _width="30px"))
    return locals()

def exhibitsearch():
    grid = None
    form2=FORM("",INPUT(_type="text",_name="lastname",requires=IS_LENGTH(minsize=3), _placeholder="Name", _size="35", _style="font-size:15px"),BUTTON("Submit", _type="submit",_value="Submit", _class="btn btn-success"))
    if form2.process(session=None, formname='form2').accepted:
        formvalue = form2.vars.lastname.strip(' \t\n\r')
        rows = ((db2.Employer.EMPLOYER_NAME.like('%' + formvalue.upper() + '%')))
        links = [lambda row: A('Select!', _href=URL('default','exhibit',args=row.EMPLOYER_CODE), _class="btn btn-success btn-xs")]
        grid = SQLFORM.grid(rows, links=links, buttons_placement='left',links_placement='left', deletable=False, create=False, details=False,searchable=False, args=request.args[:1], editable=False)
    return locals()

def exhibit():
    arg = request.args(0)
    form = SQLFORM(db2.GAD_EMPLOYER_EXHIBIT_A)
    form.vars.employerid = arg
    if form.process(session=None, formname='form2').accepted:
        response.flash = 'Record Added'
    query = ((db2.GAD_EMPLOYER_EXHIBIT_A.employerid==arg))
    grid = SQLFORM.grid(query, buttons_placement='left', links_placement='left', deletable=False, create=False, editable=False,
                        searchable=False,csv=False,args=request.args[:1])
    return locals()

@auth.requires_login()
def index():
    return dict()
@auth.requires_login()
def index2():
    code = request.args(0)
    #& (db2.Member.MEMBER_TABLE_ID==db2.Member_Payment_Date.MEMBER_TABLE_ID) db2.Member_Payment_Date.on(db2.Member.MEMBER_TABLE_ID==db2.Member_Payment_Date.MEMBER_TABLE_ID) , db2.Member_Payment_Date.PAID_THRU_DATE
    rows = db2((db2.Member.EMPLOYER_CODE==code)  & ( (db2.Member.MEMBER_STATUS_CODE == 'A') | (db2.Member.MEMBER_STATUS_CODE == 'IP' ))).select(db2.Member.FIRST_NAME, db2.Member.LAST_NAME, db2.Member.JOB_CLASS_CODE, db2.Member.DUES_CHECKOFF, db2.WORK_PERMIT.PORTABILITY_AGREEMENT_CODE, db2.WORK_PERMIT.PERMIT_EXPIRATION_DATE, db2.Member.LOCAL_CODE, left=[db2.EMPLOYMENT_HISTORY.on(db2.Member.MEMBER_TABLE_ID==db2.EMPLOYMENT_HISTORY.MEMBER_TABLE_ID), db2.QUALIFIED_BOOKS.on(db2.Member.MEMBER_TABLE_ID==db2.QUALIFIED_BOOKS.MEMBER_TABLE_ID),db2.WORK_PERMIT.on(db2.EMPLOYMENT_HISTORY.EMPLOYMENT_HISTORY_TABLE_ID==db2.WORK_PERMIT.EMPLOYMENT_HISTORY_TABLE_ID)], distinct=True)
    return dict(rows=rows)

@auth.requires_login()
def gad_ip_journal():
    #Main Program Logic...
    today = date.today()
    #Find all IP members
    #query = ((db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID == db2.MEMBER_TRANSACTION.MEMBER_TABLE_ID) & (db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID == db2.EIT_DEDUCTION.MEMBER_TABLE_ID) & (db2.GAD_IP_JOURNAL.MEMBER_STATUS_CODE == 'IP'))
    #fields = (db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.MEMBER_STATUS_CODE, db2.MEMBER_TRANSACTION.TRANSACTION_DATE, db2.EIT_DEDUCTION.WORK_DATE, db2.EIT_DEDUCTION.GROSS_WAGES, db2.EIT_DEDUCTION.DEDUCTION_AMOUNT)
    default_sort_order=[db2.GAD_IP_JOURNAL.LAST_NAME]
    #wage_sum = db2.EIT_DEDUCTION.GROSS_WAGES.sum()
    #deduction_sum = db2.EIT_DEDUCTION.DEDUCTION_AMOUNT.sum()
    #ip_members = db2((db2.MEMBER_TRANSACTION.TRANSACTION_DATE > '06/01/2014') & ((db2.EIT_DEDUCTION.GROSS_WAGES != None) | (db2.EIT_DEDUCTION.DEDUCTION_AMOUNT != None))).select(db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID, db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.LAST_NAME, db2.EIT_DEDUCTION.GROSS_WAGES.sum(), db2.EIT_DEDUCTION.DEDUCTION_AMOUNT.sum(), left=[db2.MEMBER_TRANSACTION.on(db2.MEMBER_TRANSACTION.MEMBER_TABLE_ID == db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID),db2.EIT_DEDUCTION.on(db2.EIT_DEDUCTION.MEMBER_TABLE_ID == db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID)],orderby=[db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID, db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.LAST_NAME], groupby=[db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID, db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.LAST_NAME])
    ip_members = db2(db2.MEMBER_TRANSACTION.TRANSACTION_DATE > '06/01/2014').select(db2.Member.MEMBER_TABLE_ID, db2.Member.MEMBER_ID, db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.LAST_NAME, db2.Employer.EMPLOYER_NAME, db2.MEMBER_TRANSACTION.TRANSACTION_DATE, db2.EIT_DEDUCTION.WORK_DATE, db2.EIT_DEDUCTION.GROSS_WAGES, db2.EIT_DEDUCTION.DEDUCTION_AMOUNT, 
                              left=[db2.Member.on(db2.Member.MEMBER_TABLE_ID == db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID),db2.MEMBER_TRANSACTION.on(db2.MEMBER_TRANSACTION.MEMBER_TABLE_ID == db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID),db2.EIT_DEDUCTION.on(db2.EIT_DEDUCTION.MEMBER_TABLE_ID == db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID)],orderby=[db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID, db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.LAST_NAME])
    #for member in ip_members:
        #oneMember = db2(db2.MEMBER_TRANSACTION.TRANSACTION_DATE > '06/01/2014').select(db2.Member.MEMBER_TABLE_ID, db2.Member.MEMBER_ID, db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.LAST_NAME, db2.MEMBER_TRANSACTION.TRANSACTION_DATE, db2.EIT_DEDUCTION.WORK_DATE, db2.EIT_DEDUCTION.GROSS_WAGES, db2.EIT_DEDUCTION.DEDUCTION_AMOUNT, left=[db2.Member.on(db2.Member.MEMBER_TABLE_ID == member.Member.MEMBER_TABLE_ID),db2.MEMBER_TRANSACTION.on(db2.MEMBER_TRANSACTION.MEMBER_TABLE_ID == db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID),db2.EIT_DEDUCTION.on(db2.EIT_DEDUCTION.MEMBER_TABLE_ID == db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID)],orderby=[db2.GAD_IP_JOURNAL.MEMBER_TABLE_ID, db2.GAD_IP_JOURNAL.FIRST_NAME, db2.GAD_IP_JOURNAL.MI, db2.GAD_IP_JOURNAL.LAST_NAME])
    return dict(ip_members=ip_members)

@auth.requires_login()
def test_search():
    '''grid = None
    code = request.args(0)
    fields = [db2.Member.FIRST_NAME, db2.Member.LAST_NAME]
    rows5 = ((db2.Member.MEMBER_TABLE_ID==code) & ((db2.Member.MEMBER_STATUS_CODE == 'A') | (db2.Member.MEMBER_STATUS_CODE == 'IP' )))
    grid = SQLFORM.grid(rows5, fields=fields, paginate=150, deletable=False, editable=False, create=False, user_signature=True, buttons_placement = 'left', links_placement = 'left', searchable=False, maxtextlength=100, formstyle='bootstrap')
    grid.element('th', replace=TH(' ', _class='xyz', _width="30px"))
    grid.elements('span.buttontext', replace=lambda el: el.add_class('btn btn-success'))
    form=FORM(TABLE(TR("",INPUT(_type="text",_name="lname",_placeholder='Last Name! (Enter at least 3 Characters)',_class='form-control', requires=IS_LENGTH(minsize=3))),
                    TR("",INPUT(_type="submit",_value="SUBMIT", _class='btn btn-success btn-lrg'))))
    if form.process().accepted:
        arg = (form.vars.lname.upper())
        wslname = form.vars.lname.strip(' \t\n\r')
        #rows = db2((db2.Member.LAST_NAME.like(wslname.upper() + '%')) & ((db2.Member.MEMBER_STATUS_CODE == 'A') | (db2.Member.MEMBER_STATUS_CODE == 'IP' ))).select(db2.Member.FIRST_NAME, db2.Member.LAST_NAME, db2.Member_Payment_Date.PAID_THRU_DATE, left=[db2.Member_Payment_Date.on(db2.Member.MEMBER_TABLE_ID==db2.Member_Payment_Date.MEMBER_TABLE_ID)], distinct=True)
        rows = ((db2.Member.LAST_NAME.like(wslname.upper() + '%')) & ((db2.Member.MEMBER_STATUS_CODE == 'A') | (db2.Member.MEMBER_STATUS_CODE == 'IP' )))# & (db2.Member_Payment_Date.CHARGE_CODE == 'D'))
        fields = [db2.Member.FIRST_NAME, db2.Member.LAST_NAME, db2.Member.MEMBER_TABLE_ID]#, db2.Member_Payment_Date.PAID_THRU_DATE]
        links = [lambda row: A('View',_class='btn btn-success',_href=URL("default","test_search"))]
        grid = SQLFORM.grid(rows, fields=fields, links=links, paginate=150, deletable=False, create=False, editable=False, user_signature=True, buttons_placement = 'left', links_placement = 'left', searchable=False, maxtextlength=100, formstyle='bootstrap')
        grid.elements('span.buttontext', replace=lambda el: el.add_class('btn btn-success'))
    return dict(form=form, grid=grid)'''
    records = None
    form=FORM(TABLE(TR("",INPUT(_type="text",_name="lname",_placeholder='Last Name! (Enter at least 3 Characters)',_class='form-control', requires=IS_LENGTH(minsize=3))),
                    TR("",INPUT(_type="submit",_value="SUBMIT", _class='btn btn-success btn-lrg'))))
    if form.process().accepted:
        records = SQLTABLE(db2((db2.Member_Payment_Date.CHARGE_CODE == 'D') & (db2.Member_Payment_Date.MEMBER_TABLE_ID < 1000)).select(db2.Member_Payment_Date.PAID_THRU_DATE),headers='fieldname:capitalize')

    return dict(form=form, records=records)


@auth.requires_login()
def empnameofcon():
    import time
    from datetime import datetime
    import datetime
    code = request.args(0)
    grid=None
    db2.Member.MEMBER_STATUS_CODE.readable=False
    db2.Member.MEMBER_TABLE_ID.readable=False
    db2.Member.LAST_NAME_MIXED.readable=False
    #db2.Member_Payment_Date.PAID_THRU_DATE.represent = lambda id, r: str(db2.Member_Payment_Date.PAID_THRU_DATE).strftime('%d/%m/%Y')
    db2.Member_Payment_Date.MEMBER_TABLE_ID.represent=lambda id, r: SPAN(findpaidthru(r.MEMBER_TABLE_ID))
    db2.Member.DUES_CHECKOFF.represent= lambda id, r: SPAN(duecheck(r.DUES_CHECKOFF),_style='color:red' if r.DUES_CHECKOFF=='F' else 'color:green')
    fields = [db2.Member.FIRST_NAME, db2.Member.LAST_NAME, db2.Member_Payment_Date.PAID_THRU_DATE]
    rows5 = ((db2.Member.MEMBER_TABLE_ID==code) & ((db2.Member.MEMBER_STATUS_CODE == 'A') | (db2.Member.MEMBER_STATUS_CODE == 'IP' )) & (db2.Member_Payment_Date.MEMBER_TABLE_ID == db2.Member.MEMBER_TABLE_ID))
    grid = SQLFORM.grid(rows5, fields=fields, paginate=150, deletable=False, editable=False, create=False, user_signature=True, buttons_placement = 'left', links_placement = 'left', searchable=False, maxtextlength=100, formstyle='bootstrap' )
    grid.element('th', replace=TH(' ', _class='xyz', _width="30px"))
    grid.elements('span.buttontext', replace=lambda el: el.add_class('btn btn-success'))
    form=FORM(TABLE(TR("",INPUT(_type="text",_name="lname",_placeholder='Last Name! (Enter at least 3 Characters)',_class='form-control', requires=IS_LENGTH(minsize=3))),
                    TR("",INPUT(_type="submit",_value="SUBMIT", _class='btn btn-success btn-lrg'))))
    if form.process(session=None, formname='form').accepted:
        response.flash="form accepted"
        argy = (form.vars.lname.upper())
        wslname = form.vars.lname.strip(' \t\n\r')
        rows3 = ((db2.Member.LAST_NAME.like(wslname.upper() + '%')) & ((db2.Member.MEMBER_STATUS_CODE == 'A') | (db2.Member.MEMBER_STATUS_CODE == 'IP' )) & (db2.Member_Payment_Date.MEMBER_TABLE_ID == db2.Member.MEMBER_TABLE_ID) & (db2.Member_Payment_Date.CHARGE_CODE == 'D'))
        grid = SQLFORM.grid(rows3, fields=fields, paginate=150, deletable=False, create=False, editable=False, user_signature=True, buttons_placement = 'left', links_placement = 'left', searchable=False, maxtextlength=100, formstyle='bootstrap')
        grid.element('th', replace=TH(' ', _class='xyz', _width="30px"))
        grid.elements('span.buttontext', replace=lambda el: el.add_class('btn btn-success'))
    elif form.errors:
        response.flash="form is invalid"
    else:
        response.flash=""
    rows3 = ((db2.Member.LAST_NAME==code) & (db2.Member.MEMBER_STATUS_CODE == 'A'))
    fields = [db2.Member.FIRST_NAME, db2.Member.LAST_NAME, db2.Member_Payment_Date.PAID_THRU_DATE]
    return dict(form=form, grid=grid)
@auth.requires_login()
def contractorsearch():
    code = request.args(0)
    grid=None
    links = [lambda row: A('View Members',_class='btn btn-success', _href=URL("default","index2", args=[row.EMPLOYER_CODE]))]
    fields2 = [db2.Employer.EMPLOYER_NAME]
    form2=FORM(TABLE(TR("",INPUT(_type="text",_placeholder='Con Name! (Enter at least 3 Characters)',_name="conname",_class='form-control', requires=IS_LENGTH(minsize=3))),
                    TR("",INPUT(_type="submit",_value="SUBMIT", _class='btn btn-success btn-lrg'))))
    headers2 = {'Employer.EMPLOYER_NAME':   'Name' }
    rows2 = ((db2.Employer.EMPLOYER_CODE==code) & (db2.Employer.INACTIVE_RECORD=='F'))
    grid = SQLFORM.grid(rows2, fields=fields2, paginate=150, deletable=False, create=False, editable=False, links=links, headers=headers2, buttons_placement = 'left', links_placement = 'left', searchable=False, maxtextlength=100, formstyle='bootstrap')
    grid.element('th', replace=TH(' ', _class='xyz', _width="30px"))
    grid.elements('span.buttontext', replace=lambda el: el.add_class('btn btn-success'))
    if form2.process(session=None, formname='form2').accepted:
        response.flash='form accepted'
        links = [lambda row: A('View Members',_class='btn btn-success',_href=URL("default","index2", args=[row.EMPLOYER_CODE]))]
        fields2 = [db2.Employer.EMPLOYER_NAME, db2.Employer.EMPLOYER_CODE]
        wsconname = form2.vars.conname.strip(' \t\n\r')
        rows = ((db2.Employer.EMPLOYER_NAME.like('%' + wsconname.upper() + '%')) & (db2.Employer.INACTIVE_RECORD=='F'))
        grid = SQLFORM.grid(rows, fields=fields2, paginate=150, deletable=False, create=False, editable=False, links=links, headers=headers2, buttons_placement = 'left', links_placement = 'left', searchable=False, maxtextlength=100, formstyle='bootstrap')
        grid.element('th', replace=TH(' ', _class='xyz', _width="30px"))
        grid.elements('span.buttontext', replace=lambda el: el.add_class('btn btn-success'))
    elif form2.errors:
        response.flash='form is invalid'
    else:
        response.flash=''
    return dict(form=form2, grid=grid)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())
