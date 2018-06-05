'''
Created on Jan 18, 2018

@author: loitg
'''
from textgen.items import *
from textgen.combiner import *
from textgen.detailgen import *
import copy
from utils.params import clconfig

#Bo sung malls, streets
#Ngay thang nam
#keypair, id chua lam


MALL_SUFFIX = [
    'SHOPPING CENTRE',
    'SHOPPING CTR',
    ]

MALLS = [
    'Tampines Mall',
    'TAMPINES CENTRAL',
    'STAR VISTA',
    'The Star Vista',
    'IMM BUILDING',
    'IMM MALL',
    'IMM BRANCH',
    'IMM BLDG',
    'BUKIT PANJANG PLAZA',
    'LOT 1',
    'LOT ONE',
    'JUNCTION 8',
    'BEDOK',
    'BEDOK MALL',
    'WESTGATE',
    'Sembawang',
    'PLAZA SINGAPURA',
    'BUGIS JUNCTION',
    'BUGIS PLUS',
    'RAFFLES CITY',
    'JCUBE'
    ]

STREET = [
    'TAMPINES CENTRAL', #4 
    'VISTA EXCHANGE GREEN', #1
    'JELEBU ROAD', #1
    'BISHAN PLACE', #9
    'NEW UPPER CHANGI', #311
    'GATEWAY DRIVE', #3
    'JURONG EAST CENTRAL', #2
    'SEMBAWANG', #604
    'ORCHARD ROAD', #68
    'VICTORIA', #201
    'VICTORIA', #230
    'NORTH BRIDGE'
    ]

LOCATIONS = [
    'CHOA CHU KANG'
    ]

RECEIPT_ID_KEYS = [
    'TRANS',
    'CHK',
    'Bill',
    'Trans',
    'Check',
    'Receipt',
    'Rcpt',
    'COUNTER',
    'Order',
    'Invoice',
    'Tax Invoice',
    'Serial',
    'Sales'
    ]

TOTAL_KEYS = [
    'Grand Total',
    #'SUBTOTAL',
    'Total  $',
    'Total',
    'INVOICE TOTAL', 
    'PURCHASE AMOUNT',
    'Amount paid',
    'Amount',
    'TOTAL S$',
    'Net Total',
    'Total Payable',
    'TOTAL AMOUNT',
    'NET SALES',
    'Total Due',
    'Total (SGD)',
    'Cash',
    'Nets'
    ]

class CapitalandGen(Gen):
    def __init__(self):
        self.rphonefax0 = r'\d{4}[ -]\d{4}|\d{8}'
        self.rphonefax1 = r'\+65-\d{4}[ -]\d{4}|(65)\d{8}'
        self.rgst = r'(M(\d|R)|19|20)-?\d{7}-?[A-Z0-9]'
        rmoney0 = r'\$?[1-9]?\d\.\d0'
        rmoney1 = r'\$?[1-9]\d\d?\.\d\d' #, 'SGD'
        moneyval = ListGenWithProb([rmoney0, rmoney1], [0.3,0.7])
        self.moneyval = ComplexGen([ListGenWithProb(['','$','$ ','S$[ ]?','SGD'],[0.3,0.4,0.2,0.05,0.05]), moneyval, '[ ]?SGD'],[0.5,1.0,0.1])
        self.rid0 = r'[A-Z]{0,3}0?0?0?\d{2,8}'
        self.rid1 = r'\d{2,12}'
        self.rid2 = r'\d{2,5}[- ]\d{2,5}[- ]\d{2,5}'
        self.rid3 = r'[A-Z]{0,3}[\d-]{3,18}[A-Z]{0,3}'
        self.idval = ListGenWithProb([self.rid0, self.rid1, self.rid2, self.rid3],[0.4, 0.4, 0.1, 0.1])
        self.number = ListGenWithProb([r'[0-9]', r'[1-9][0-9]', r'[1-9][0-9]{2}'],[0.5,0.2,0.3])
        self.createStore()
        self.createAddr()
        self.createBlock()
        self.createDateTime()
        self.createIDPair()
        self.createLocationPair()
        self.createMall()
        self.createNotPair()
        self.createPair()
        self.createTotalPair()
        self.createZipcode()
        self.createSpecialItem()
        self.createGen()
    
    def createIDPair(self):
        rawidkey = StringListGen(RECEIPT_ID_KEYS)
        idsuffix = ListGenWithProb([r'[ ]No\.?', r'[ ]number',r'[ ]?#'], [0.5,0.1,0.4])
        idkey = ComplexGen([rawidkey, idsuffix],[1.0,0.6])
        self.idkey = ChangeCaseGen(idkey, 0.75, 0.0)
        self.idpair = PairGen(self.idkey, self.idval, 0.4, 0.3, 0.3, ':', True, True)
        return self.idpair
    
    def createLocationPair(self):
        regno = ChangeCaseGen(ComplexGen([r'reg(\.|istration)?', r' no\.?'], [0.9, 0.6]), 0.75, 0.0)
        self.gstkey = ComplexGen([r'GST[ ]', regno], [1.0,0.9])
        self.gstval = RegExGen(self.rgst)
        self.gstpair = PairGen(self.gstkey, self.gstval, 0.7, 0.15, 0.15, ':', True, False)
        
        telfaxkey = RegExGen(r'(tel|fax)[ ](no\.?)?')
        telfaxkey = ListGenWithProb([telfaxkey, 'phone', 'hotline'], [0.8,0.1,0.1])
        self.telfaxkey = ChangeCaseGen(telfaxkey, 0.75, 0.0)
        self.telfaxval = ListGenWithProb([self.rphonefax0, self.rphonefax1],[0.7,0.3])
        self.telfaxpair = PairGen(self.telfaxkey, self.telfaxval, 0.7, 0.15, 0.15, ':', True, False)
        
        self.companykey = ChangeCaseGen(ComplexGen([r'(UEN[ ]|Company[ ]|Co\.?[ ]|Bus[ ]|Biz[ ])',r'reg(\.|istration)?', r' no\.?'], [1.0, 0.9, 0.6]), 0.75, 0.0)
        self.companyval = RegExGen(r'\d{9}[A-Z]') #future: regex format
        self.companypair = PairGen(self.companykey, self.companyval, 0.7, 0.15, 0.15, ':', True, False)
                
        
    def createPair(self):
        tablekey =  RegExGen(r'(table|tbl)[ ](no\.)?')
        self.tablepair = PairGen(ChangeCaseGen(tablekey, 0.75, 0.0), self.number, 0.4, 0.3, 0.3,':', False, False)
        ####
        namekey = StringListGen(['name', 'waiter','staff', 'cashier', 'operator', 'ordered by' ,'customer', 'first name', 'last name','guest','svr' ])
        self.namepair = PairGen(namekey, NameGen(), 0.4, 0.3, 0.3,':',True, True)
        self.namepair = ChangeCaseGen(self.namepair, 0.75, 0.0)
        ####
        otherkey = StringListGen(['station','pax','slip','cover','membership','pos','pos no','pos title','POS Terminal No','invoice type','card number','status',
                              'register', 'auth', 'Plu#','transaction type','acnt no\.'])
        self.otherpair = PairGen(ChangeCaseGen(otherkey, 0.75, 0.0), self.idval, 0.4, 0.3, 0.3,':', True, True)#future: idval not for this
        ####
        moneykey = StringListGen(['total savings','subtotal', 'sub total', 'subttl', 'card disc', 'total disc', 'rounding', 'mst/visa', 'change',
                              'change due', 'visa', 'credit card visa', 'master', 'visa/master xxxx', 'Service Tax (10%)', '10% Svr Chrg',
                              '10% SVC CHG', '10% Service Charge', 'Service Charge 10.00%','Service Chg(10%)', 'Service Charge', 'SvCharge',
                              'Payable', 'Tender VISA', 'Avg. Pax', 'Rounding Adj.', 'GST 7%', '7% GST', 'GST 7.00%', 'GST ( 7% )', 'GST CHARGES 7%', '7% GST Inclusive'])
        self.moneykey = ChangeCaseGen(moneykey, 0.5, 0.0)
        self.moneypair = PairGen(self.moneykey, self.moneyval, 0.2, 0.4, 0.4, ':', True, True)
        
    
    def createTotalPair(self):
        self.totalkey = ChangeCaseGen(StringListGen(TOTAL_KEYS), 0.5, 0.0)
        self.totalpair = PairGen(self.totalkey, self.moneyval, 0.2, 0.2, 0.6, ':', True, True)
        ####
        self.nottotalkey = ChangeCaseGen(StringListGen(['total qty', 'qty', 'Total number of items', 'total pts', 'no of items',
                                                    'total items', 'total qty sold', 'pts added', 'updated pts']), 0.5, 0.0)
        self.nottotalpair = PairGen(self.nottotalkey, self.number, 0.8, 0.1, 0.1, ':', True, True)
        
    def createNotPair(self):
        notpair = ParragraphGen('/home/loitg/workspace/genreceipt/resource/parragraph.txt')
        self.notpair = ChangeCaseGen(notpair, 0.3, 0.0)
        return self.notpair
    
    
    def createStore(self):
        self.rawstore = StoreGen('/home/loitg/workspace/genreceipt/resource/store.txt')
        rsinprefix = r'\(S\)|S|SE|SG|Singapore|SINGAPORE|Sing|S\'PORE|SIN|Sin'
        store_suffix = ListGenWithProb([r'\[BM\]', r'(' + rsinprefix + ')? Pte Ltd'],[0.2,0.8])
        storegen = ComplexGen([self.rawstore, ' ', store_suffix], [1.0,1.0,0.3])
        self.store = ChangeCaseGen(storegen, 0.75, 0.0)
        return self.store
        
    
    def createZipcode(self):
        rprefix = r'\(S\)|S|SE|SG|Singapore|SINGAPORE|Sing|S\'PORE|SIN|Sin'
        rzc = r'\d{6}'
        self.zipcode = BlankSpaceConbiner(RegExGen(rprefix), RegExGen(rzc))
        return self.zipcode
    
    def createBlock(self):
        numbergen = ListGenWithProb([r'[\dB]\d', r'[A-Z]\d', r'[A-Z0-9]\d\d'], [0.9, 0.05, 0.05])
        temp0 = KeyValueCombiner(StringGen('/'), numbergen, StringGen(''))
        temp1 = ComplexGen([numbergen,r'\-', numbergen, temp0],
                           [1.0,1.0,1.0,0.1])
        temp2 = KeyValueCombiner(StringGen('&'), temp1, StringGen(''))
        self.block = ComplexGen([r'\#', temp1, temp2],
                                  [1.0,1.0,0.1])
        return self.block
    
    def createMall(self):
        self.rawmall = StringListGen(MALLS)
        mall_suffix = RegExGen(r'(Shopping Center|Shopping Ctr|Shoppers Mall)')
        mallgen = ComplexGen([BlankSpaceConbiner(self.rawstore, StringGen('@')), self.rawmall, ' ', mall_suffix], [0.02,1.0,1.0,0.3])
        self.mall = ChangeCaseGen(mallgen, 0.75, 0.0)
        return self.mall
        
    def createAddr(self):
        addr = ComplexGen([r'No\.?[ ]', self.number,',?[ ]', StringListGen(STREET), ' ', r'(ST|ROAD|Ave( \d)?|0\d|\d\d)'],
                               [0.2, 1.0, 1.0, 1.0, 1.0,0.4])
        self.addr = ChangeCaseGen(addr, 0.75, 0.0)
        return self.addr

    def createDateTime(self):
        dat = ComplexGen([KeyValueCombiner('D(ate|ATE)', SepGen(':', allowBlank=True, allowFar=True), ''), DateGen(todate='2018-12-31', dateformat=clconfig.date), ' ', TimeGen()], [0.4, 1.0, 1.0, 0.4])
        dat = ComplexGen(['------',dat,'------'],[1.0,1.0,1.0])
        dat_giotruoc = ComplexGen([KeyValueCombiner('D(ate|ATE)', SepGen(':', allowBlank=True, allowFar=True),''), TimeGen(), ' ', DateGen(todate='2018-12-31', dateformat=clconfig.date)], [0.4, 0.4, 1.0, 1.0])
        tim = ComplexGen([KeyValueCombiner('T(ime|IME)', SepGen(':', allowBlank=True, allowFar=True),''), TimeGen()], [0.7, 1.0])
        self.datetime = ListGenWithProb([dat, dat_giotruoc, tim], [0.5, 0.2, 0.3])
        return self.datetime

    def createSpecialItem(self): #For tampines
        r0 = RegExGen(r'St:[\w\d]{3,5}[ ]{2,6}Rg:\d{1,3}[ ]{2,5}Ch:\d{3,10}[ ]{2,5}Tr:\d{2,9}')
        r1 = CL0Gen()
        self.special = ListGenWithProb([r0,r1],[0.5,0.5])
        return self.special
        
    
    def createGen(self):
        list_loc = [self.addr, self.block, self.mall, self. zipcode]
        self.locgen13 = PermutationCombiner(list_loc, SepGen(',', allowBlank=True, allowFar=False), 1, 3) #3%
        
        list_lockeyval = [self.gstpair, self.telfaxpair, self.companyval]
        self.locpairgen2 = PermutationCombiner(list_lockeyval, SepGen(',', allowBlank=True, allowFar=False), 2)
        self.gsttelcomp = ListGenWithProb([self.locpairgen2, self.gstpair, self.telfaxpair, self.companypair],
                                     [0.4        ,0.4          ,0.1             ,0.1              ]) #3%
        
        self.store #3%
        
        self.datetime #31%
        
        self.totalpair #20%
        self.nottotalpair #15%
        self.idpair #6%
        self.notpair #2%
        self.others = ListGenWithProb([self.tablepair, self.namepair, self.otherpair, self.moneypair],
                                                                  [0.1, 0.1, 0.1, 0.7]) #5%
        
        list_dateid = [self.datetime, self.idpair, self.others]
        self.dateidgen2 = PermutationCombiner(list_dateid, RegExGen('[ ]{1,3}'), 2) #10%
        self.special #2%
        
        self.gener = ListGenWithProb([self.locgen13, self.gsttelcomp,self.store,self.datetime,self.totalpair, self.nottotalpair, self.idpair, self.notpair, self.others, self.dateidgen2, self.special],\
                                    [0.03         ,0.03            ,0.03     ,0.31          ,0.20          ,0.15             ,0.06        ,0.02         ,0.05        ,0.1             ,0.02         ])

    def gen(self):
        txt = self.gener.gen()
        l = len(txt)
        numspaces = np.random.randint(1,5)
        if np.random.rand() < 0.12:
            txt = ' '*numspaces + txt 
        if np.random.rand() < 0.12:
            txt = txt  + ' '*numspaces
        if np.random.rand() < 0.2 and l > 15:
            startindex = np.random.randint(l-15 + 1)
            txt = txt[startindex:(startindex+15)]
        return txt
        
if __name__ == '__main__':
    clgen = CapitalandGen()
    for i in range(200):
        print '---' + clgen.datetime.gen() + '---'





