import os
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import IntVar, StringVar, BooleanVar
from tkinter import messagebox

from config import *
from model import *
from util import *
from kiwoom import *
from stock import *


class MyApp:
    def __init__(self):
        Model.load()
        self.stocklist = None
        self.kiwoom = None

        self.root = tk.Tk()
        self.init(self.root)

    def run(self):
        self.root.mainloop()


    def init(self, root):
        root.title(APP_NAME)
        self.init_left_frame()
        self.init_right_frame()
        self.adjust_ui()


    def init_left_frame(self):
        left_frame = tk.Frame(self.root, width=400)
        left_frame.pack(side='left', fill='y')

        self.init_select_frame(left_frame)
        self.init_userinfo_frame(left_frame)
        self.init_register_frame(left_frame)


    def init_right_frame(self):
        right_frame = tk.Frame(self.root, width=624)
        right_frame.pack(side='left', fill='y')

        self.init_order_frame(right_frame)
        self.init_order_status_frame(right_frame)
        self.init_my_balance_frame(right_frame)


    def init_order_frame(self, frame):
        self.order_market_value = StringVar()
        self.order_name_value = StringVar()
        self.order_code_value = StringVar()
        self.order_qty_value = StringVar()
        self.order_uv_value = StringVar()

        UxUtil.init_label(frame, '주식 매수주문')
        order_block = tk.Frame(frame, bd=1, relief='solid', padx=10, pady=10)
        order_block.pack(padx=10, fill='x')
        tk.Label(order_block, text='거래소:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE)).grid(row=0, column=0, padx=5)
        tk.Radiobutton(order_block, text=KRX, value=KRX, variable=self.order_market_value, command=lambda: self.buy_market_select(self.order_market_value)).grid(row=0, column=1, sticky='w')
        tk.Radiobutton(order_block, text=NXT, value=NXT, variable=self.order_market_value, command=lambda: self.buy_market_select(self.order_market_value)).grid(row=0, column=2, sticky='w')
        tk.Radiobutton(order_block, text=SOR, value=SOR, variable=self.order_market_value, command=lambda: self.buy_market_select(self.order_market_value)).grid(row=0, column=3, sticky='w')

        self.order_market_value.set(KRX)

        combo_options = ['보통', '시장가', '단일가', '보통(IOC)', '시장가(IOC)', '보통(FOK)', '시장가(FOK)']
        combo_options_value = ['0', '3', '62', '10', '13', '20', '23']

        line = tk.Frame(frame)
        #line.pack()
        tk.Label(order_block, text='종목명:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE)).grid(row=1, column=0, padx=5)
        stock_name = tk.Entry(order_block, textvariable=self.order_name_value, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), width=30)
        stock_name.grid(row=1, column=1, padx=5)
        tk.Label(order_block, text='종목코드:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE)).grid(row=2, column=0, padx=5)
        stock_code = tk.Entry(order_block, textvariable=self.order_code_value, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), width=30)
        stock_code.grid(row=2, column=1, padx=5)
        tk.Label(order_block, text='주문수량:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE)).grid(row=3, column=0, padx=5)
        tk.Entry(order_block, textvariable=self.order_qty_value, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), width=30).grid(row=3, column=1, padx=5)
        tk.Label(order_block, text='주문단가:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE)).grid(row=4, column=0, padx=5)
        tk.Entry(order_block, textvariable=self.order_uv_value, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), width=30).grid(row=4, column=1, padx=5)
        tk.Label(order_block, text='매매구분:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE)).grid(row=5, column=0, padx=5)
        trade_combo = ttk.Combobox(order_block, values=combo_options, state="readonly")
        trade_combo.grid(row=5, column=1, padx=5)
        trade_combo.current(0)

        stock_name.bind("<KeyRelease>", lambda e: self.on_stock_name_release(e.widget.get()))

        line2 = tk.Frame(frame)
        line2.pack()
        buy_cmd = tk.Button(line2, text='매수하기', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), 
                        command=lambda: self.request_order('kt10000', self.order_market_value.get(), self.order_code_value.get(), self.order_qty_value.get(), self.order_uv_value.get(), combo_options_value[trade_combo.current()]))
        buy_cmd.pack(side=tk.LEFT, padx=10, pady=10)
        sell_cmd = tk.Button(line2, text='매도하기', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), 
                        command=lambda: self.request_order('kt10001', self.order_market_value.get(), self.order_code_value.get(), self.order_qty_value.get(), self.order_uv_value.get(), combo_options_value[trade_combo.current()]))
        sell_cmd.pack(side=tk.LEFT, padx=10, pady=10)

        query_pending_cmd = tk.Button(line2, text='미체결조회', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), 
                        command=lambda: self.request_pending_order())
        query_pending_cmd.pack(side=tk.LEFT, padx=10, pady=10)

        query_balance_cmd = tk.Button(line2, text='잔고조회', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), 
                        command=lambda: self.request_balance())
        query_balance_cmd.pack(side=tk.LEFT, padx=10, pady=10)        


    def init_order_status_frame(self, frame):
        line = tk.Frame(frame)
        line.pack()
        UxUtil.init_label(line, '미체결') 

        columns = ("주문번호", "종목명", "구분", "주문가", '미체결수량', '거래소')
        self.os_tree = ttk.Treeview(line, columns=columns, show="headings", selectmode="browse", height=5)
        self.os_tree.pack(anchor="w", side='left', fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        scrollbar = ttk.Scrollbar(line, orient="vertical", command=self.os_tree.yview)
        scrollbar.pack(side="right", fill="y")

        # 헤더 생성
        for col in columns:
            self.os_tree.heading(col, text=col)
            self.os_tree.column(col, anchor="center")

        self.os_tree.bind("<<TreeviewSelect>>", self.os_tree_on_select)
        self.os_tree.bind("<Double-1>", self.os_tree_on_double_click)        

    
    def update_order_status(self, data):       
        for item in self.os_tree.get_children():
            self.os_tree.delete(item)

        if data == []:
            return
        
        for item in data:
            values = (
                item.get("ord_no", ""),
                item.get("stk_nm", ""),
                item.get("trde_tp", ""),
                Util.strip_leading_zeros(item.get("ord_uv", "")),
                Util.strip_leading_zeros(item.get("ord_qty", "")),
                item.get("dmst_stex_tp", ""),
            )
            self.os_tree.insert("", tk.END, values=values)


    def os_tree_on_select(self, event):
        selected_item = self.os_tree.focus()
        if not selected_item:
            return        

        record = self.os_tree.item(selected_item, 'values')  # 튜플 형태로 가져옴
        stock = self.stocklist.find_by_name(record[1])
        if stock != None:
            self.order_code_value.set(stock.code)
        self.order_name_value.set(record[1])
        self.order_uv_value.set(Util.remove_commas(record[3]))
        self.order_qty_value.set(Util.remove_commas(record[4]))


    def os_tree_on_double_click(self, event):
        selected_item = self.os_tree.focus()
        if not selected_item:
            return        

        record = self.os_tree.item(selected_item, 'values')
        stock = self.stocklist.find_by_name(record[1])
        if stock == None:
            UxUtil.show_warning("종목정보 업데이트가 필요합니다. 재시작해주세요.")
            return
        
        self.request_cancel_order('kt10003', record[5], record[0], stock.code, Util.remove_commas(record[4]))


    def init_my_balance_frame(self, frame):
        line = tk.Frame(frame)
        line.pack()

        UxUtil.init_label(line, '잔고')

        columns = ("종목명", "매입가", "현재가", "평가손익", "수익율", "가능수량", "보유수량", )
        self.balance_tree = ttk.Treeview(line, columns=columns, show="headings", selectmode="browse")
        self.balance_tree.pack(anchor=tk.W, side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.balance_tree_sort_orders = {col: False for col in columns}

        scrollbar = ttk.Scrollbar(line, orient=tk.VERTICAL, command=self.balance_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 헤더 생성
        for col in columns:
            self.balance_tree.heading(col, text=col, command=lambda _col=col: self.balance_sort_by_column(_col))
            self.balance_tree.column(col, anchor="center")

        self.balance_tree.bind("<<TreeviewSelect>>", self.balance_tree_on_select)


    def balance_sort_by_column(self, col):
        column_map = {
            '종목명': 'stk_nm',
            '매입가': 'pur_pric',
            '현재가': 'cur_prc',
            '평가손익': 'evltv_prft',
            '수익율': 'prft_rt',
            '가능수량': 'trde_able_qty',
            '보유수량': 'rmnd_qty',
        }

        reverse = self.balance_tree_sort_orders[col]

        mapped_col = column_map.get(col, col)  # 기본값은 col        
        self.balance_data.sort(key=lambda x: x.get(mapped_col, ""), reverse=reverse)
        self.balance_tree_sort_orders[col] = not reverse
        self.update_balance_status(self.balance_data)


    def update_balance_status(self, data):       
        for item in self.balance_tree.get_children():
            self.balance_tree.delete(item)

        if data == []:
            return
        
        self.balance_data = data        
        # columns = ("종목명", "매입가", '현재가', "평가손익", "수익율", '가능수량', '보유수량', )
        for item in self.balance_data:
            values = (
                item.get("stk_nm", ""),
                Util.strip_leading_zeros(item.get("pur_pric", "")),
                Util.strip_leading_zeros(item.get("cur_prc", "")),
                Util.strip_leading_zeros(item.get("evltv_prft", "")),
                item.get("prft_rt", ""),
                Util.strip_leading_zeros(item.get("trde_able_qty", "")),
                Util.strip_leading_zeros(item.get("rmnd_qty", "")),
            )
            self.balance_tree.insert("", tk.END, values=values)


    def balance_tree_on_select(self, event):
        selected_item = self.balance_tree.focus()
        if not selected_item:
            return        

        record = self.balance_tree.item(selected_item, 'values')
        stock = self.stocklist.find_by_name(record[0])
        if stock != None:
            self.order_code_value.set(stock.code) #종목코드
        self.order_name_value.set(record[0]) # 종목명
        self.order_uv_value.set(Util.remove_commas(record[1])) # 매입가
        self.order_qty_value.set(Util.remove_commas(record[5])) # 가능수량


    def log_message(self,tag, msg):
        current = Util.today()
        message = f'[{current}][{tag}] {msg}\n'
        if DEBUG:
            print (message)


    def adjust_ui(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        self.root.geometry(f'{width}x{height}')
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = (screen_height - height) // 2
        position_left = (screen_width - width) // 2
        self.root.geometry(f'{width}x{height}+{position_left}+{position_top}')


    def init_select_frame(self, frame):
        self.appKey_value = StringVar()
        self.appSecret_value = StringVar()

        UxUtil.init_label(frame, '계정 선택')

        select_block = tk.Frame(frame, bd=1, relief='solid', padx=10, pady=10)
        select_block.pack(padx=10, fill=tk.X)
        account_label = tk.Label(select_block, text='계정:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE))
        account_label.grid(row=0, column=0, padx=5)
        options = Model.account_list()
        current = Model.current_user()
        self.combo = ttk.Combobox(select_block, values=options, state="readonly")
        if current != None:
            account = f'{current[USER_ACCOUNT]} {current[USER_NAME]}'
            if account in options:
                self.combo.current(options.index(account))

        self.combo.grid(row=0, column=1, padx=5)
        self.combo.bind("<<ComboboxSelected>>",  self.on_account_select)

        select_block = tk.Frame(frame, bd=1, relief='solid', padx=10, pady=5)
        select_block.pack(padx=10, pady=10, fill='x')

        UxUtil.init_label_entry(select_block, 'AppKey:', 1, self.appKey_value, state='readonly')
        UxUtil.init_label_entry(select_block, 'AppSecret:', 2, self.appSecret_value, state='readonly')

        line = tk.Frame(frame)
        line.pack()
        login = tk.Button(line, text='로그인하기', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), command=self.request_login)
        login.pack(side=tk.LEFT, padx=10, pady=10)

        self.update_select_user()


    def request_login(self):
        user = Model.current_user()
        if user == None:
            Util.show_warning('사용자 설정 필요')
            return
        
        self.kiwoom = Kiwoon(user[USER_APPKEY], user[USER_APPSECRET])
        params = {
            "qry_tp": "0", # 상장폐지조회구분 0:전체, 1:상장폐지종목제외
		    "dmst_stex_tp": Model.market() # 국내거래소구분 KRX:한국거래소,NXT:넥스트트레이드
	    }

        responses = self.kiwoom.request_account('kt00004', params)
        entr = Util.strip_leading_zeros(responses[0]['entr'])
        tot_est_amt = Util.strip_leading_zeros(responses[0]['tot_est_amt'])

        info = f"예수금: {entr}, 유가잔고평가액: {tot_est_amt}"
        self.info_value.set(info)

        self.log_message('login', responses[0])
        self.load_all_stocks()
        UxUtil.show_info('로그인 성공')

    
    def request_pending_order(self):
        if self.kiwoom == None:
            UxUtil.show_warning('로그인이 필요합니다.')
            return

    	# 2. 요청 데이터
        params = {
		    'ord_dt': Util.today_date(), # 주문일자 YYYYMMDD
            'qry_tp': '3', # 조회구분 1:주문순, 2:역순, 3:미체결, 4:체결내역만
            'stk_bond_tp': '0', # 주식채권구분 0:전체, 1:주식, 2:채권
            'sell_tp': '0', # 매도수구분 0:전체, 1:매도, 2:매수
            'stk_cd': '', # 종목코드 공백허용 (공백일때 전체종목)
            'fr_ord_no': '', # 시작주문번호 공백허용 (공백일때 전체주문)
            'dmst_stex_tp': '%', # 국내거래소구분 %:(전체),KRX:한국거래소,NXT:넥스트트레이드,SOR:최선주문집행
        }

        responses = self.kiwoom.request_account('kt00007', params)

        data = []
        for response in responses:
            records = response['acnt_ord_cntr_prps_dtl']
            for record in records:
                d = { "ord_no": record['ord_no'], 
                     "stk_cd": record['stk_cd'],
                     "stk_nm": record['stk_nm'],
                     "trde_tp": record['trde_tp'],
                     "ord_qty": record['ord_qty'],
                     "ord_uv": record['ord_uv'],
                     "dmst_stex_tp": record['dmst_stex_tp']
                }
                data.append(d)

        self.log_message('request_pending_order', data)

        self.update_order_status(data)


    def request_balance(self):
        if self.kiwoom == None:
            UxUtil.show_warning('로그인이 필요합니다.')
            return
                                
        params = {
            "qry_tp": "1", # 상장폐지조회구분 0:전체, 1:상장폐지종목제외
		    "dmst_stex_tp": Model.market() # 국내거래소구분 KRX:한국거래소,NXT:넥스트트레이드
	    }

        responses = self.kiwoom.request_account('kt00018', params)
        
        data = []
        for response in responses:
            records = response['acnt_evlt_remn_indv_tot']
            for record in records:
                d = {
                     "stk_cd": record['stk_cd'], 
                     "stk_nm": record['stk_nm'],
                     "pur_pric": record['pur_pric'], # 매입가
                     "cur_prc": record['cur_prc'], # 현재가
                     "evltv_prft": record['evltv_prft'], # 손익금액
                     "prft_rt": record['prft_rt'],  #손익율
                     "trde_able_qty": record['trde_able_qty'], #가능수량
                     "rmnd_qty": record['rmnd_qty'], # 보유수량
                }
                data.append(d)

        self.log_message('request_balance', data)
        self.update_balance_status(data)

    def request_order(self, cmd, market, code, qty, uv, trade):
        if self.kiwoom == None:
            UxUtil.show_warning('로그인이 필요합니다.')
            return

        if not self.kiwoom.is_valid_order(code, qty, uv):
            UxUtil.show_warning(f'주문을 확인하세요. {code} {qty} {uv}')
            return
                        
        yesNo = UxUtil.show_confirm('확인', f'주문하시겠습니까?')
        if not yesNo:
            return

        params = {
            "dmst_stex_tp": market,
            "stk_cd": code,
            "ord_qty": qty,
            "ord_uv": uv,
            "trde_tp": trade,
            "cond_uv": "", # 조건단가 
        }

        responses = self.kiwoom.request_order(cmd, params)
        self.log_message('order', responses[0])
        UxUtil.show_info(responses[0]['return_msg'])


    def request_cancel_order(self, cmd, market, order, code, qty):
        if self.kiwoom == None:
            UxUtil.show_warning('로그인이 필요합니다.')
            return
                                
        yesNo = UxUtil.show_confirm('확인', f'주문을 취소 하시겠습니까?')
        if not yesNo:
            return

        params = {
            "dmst_stex_tp": market,
            "orig_ord_no": order,
            "stk_cd": code,
            "cncl_qty": qty,
        }

        responses = self.kiwoom.request_order(cmd, params)
        self.log_message('cancel_order', responses[0])
        UxUtil.show_info(responses[0]['return_msg'])
        self.request_pending_order()


    def load_all_stocks(self):
        if self.stocklist != None:
            return
        self.stocklist = StockList()

        markets = ['0', '10']
        for market in markets:            
            responses = self.kiwoom.request_stocklist(market)
            for res in responses:
                list = res['list']
                for item in list:
                    self.stocklist.add(Stock('0', item['code'], item['name']))


    def update_select_user(self):
        user = Model.current_user()
        if user == None:
            return
        self.appKey_value.set(user[USER_APPKEY])
        self.appSecret_value.set(user[USER_APPSECRET])        


    def init_userinfo_frame(self, frame):
        market_value = StringVar()
        self.info_value = StringVar()

        UxUtil.init_label(frame, '계좌 정보')

        select_block = tk.Frame(frame, bd=1, relief='solid', padx=10, pady=10)
        select_block.pack(padx=10, fill='x')

        market_label = tk.Label(select_block, text='거래소 구분:', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE))
        market_label.grid(row=0, column=0, padx=5)
        btn_krx = tk.Radiobutton(select_block, text=KRX, value=KRX, variable=market_value, command=lambda: self.market_select(market_value))
        btn_krx.grid(row=0, column=1, sticky='w')
        btn_nxt = tk.Radiobutton(select_block, text=NXT, value=NXT, variable=market_value, command=lambda: self.market_select(market_value))
        btn_nxt.grid(row=0, column=2, sticky='w')
        market_value.set(KRX)

        line = tk.Frame(frame)
        line.pack()

        info_entry = tk.Entry(line, state='readonly', textvariable=self.info_value, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), width=60)
        info_entry.pack(side=tk.LEFT, padx=10, pady=10)


    def init_register_frame(self, frame):
        r_name_value = StringVar()
        r_account_value = StringVar()
        r_appKey_value = StringVar()
        r_appSecret_value = StringVar()

        UxUtil.init_label(frame, '계정 등록')

        regist_block = tk.Frame(frame, bd=1, relief='solid', padx=10, pady=10)
        regist_block.pack(padx=10, fill='x')

        UxUtil.init_label_entry(regist_block, '이름:', 0, r_name_value)
        UxUtil.init_label_entry(regist_block, '계정:', 1, r_account_value)
        UxUtil.init_label_entry(regist_block, 'AppKey:', 2, r_appKey_value)
        UxUtil.init_label_entry(regist_block, 'AppSecret:', 3, r_appSecret_value)

        line = tk.Frame(frame)
        line.pack()
        regist = tk.Button(line, text='신규 등록하기', font=(DEFAULT_FONT, DEFAULT_FONT_SIZE),
                        command=lambda: self.register_account(r_name_value, r_account_value, r_appKey_value, r_appSecret_value))
        regist.pack(side=tk.LEFT, padx=10, pady=10)


    def register_account(self, r_name_value, r_account_value, r_appKey_value, r_appSecret_value):
        name = r_name_value.get()
        account = r_account_value.get()
        appKey = r_appKey_value.get()
        appSecret = r_appSecret_value.get()

        if name == '' or account == '' or appKey == '' or appSecret == '':
            UxUtil.show_warning('name, account, appKey 혹은 appSecret을 입력하세요.')
            return

        if Model.find_by_user(account):
            UxUtil.show_info(f'{account} 는 이미 존재합니다.')
            return
        
        Model.add_user(name, account, appKey, appSecret)
        UxUtil.show_info('성공하였습니다..')
        self.update_select_frame()

        r_name_value.set('')
        r_account_value.set('')
        r_appKey_value.set('')
        r_appSecret_value.set('')


    def update_select_frame(self):
        self.combo['values'] = Model.account_list()
        self.update_select_user()


    def on_account_select(self, event):
        value = event.widget.get()
        parts = value.split()
        Model.set_current_account(parts[0])
        self.update_select_user()


    def on_stock_name_release(self, value):
        if self.stocklist == None:
            return
        
        stock = self.stocklist.find_by_name(value)
        if stock != None:
            self.order_code_value.set(stock.code)


    def market_select(self, market_value):
        Model.update_market(market_value.get())
       

    def buy_market_select(self, market_value):
        print (market_value.get())


def main():
    app = MyApp()
    app.run()

if __name__ == '__main__':
    main()