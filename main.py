from time import sleep
import sys, platform, threading
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import datetime
from pytz import timezone
# private modules
import felicaidm as fe
import add_nfc_2_azure as adnfc

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.master = master
        self.pack()
        self.firstDispMes = "新しく登録するカードをタッチしてください。"
        self.newWinMes = "新規ウィンドウを確認してください。"
        self.create_widgets()
    
    def create_widgets(self):
        self.fontStyle = tkFont.Font(family="System", size=26)
        self.buttonFont = tkFont.Font(family="System", size=18)
        self.textLabel = tk.Label(text=self.firstDispMes, font=self.fontStyle)
        self.textLabel.pack(side="top", expand=1)
        self.quitButton1 = tk.Button(text="キャンセルして終了", font=self.buttonFont, command=sys.exit)
        self.quitButton1.pack(fill="both")
        self.startReadNfc()

    def startReadNfc(self):
        thread1 = threading.Thread(target=self.aboutNfc)
        thread1.setDaemon(True)
        thread1.start()
        

    def aboutNfc(self):
        self.cardID = fe.inputCard()
        if self.cardID == None:
            displayText = "対応していないカードです。\n他のカードを試してください。"
            self.openMessageDialog(titleText="メッセージ", displayText=displayText, buttonText="閉じる")
            return

        authInfo = adnfc.resolve_crew(card_hash=self.cardID)
        if authInfo is None:
            self.inputInfoDialog("新規クルー情報入力")
        else:
            displayText = "このカードは既に登録されています。別のカードを試してください。\n身に覚えがない時は管理者に相談してください。"
            del self.cardID
            self.openMessageDialog(titleText="メッセージ",displayText=displayText, buttonText="閉じる")
        

    def openDialog(self, titleText):
        self.dialog = tk.Toplevel(self)
        self.dialog.title(titleText)
        zoomer(self.dialog)
        self.dialog.grab_set()

    def openMessageDialog(self, titleText, displayText, buttonText):
        self.openDialog(titleText=titleText)
        self.textLabel = tk.Label(master=self.dialog, text=displayText, font=self.fontStyle)
        self.textLabel.pack(expand=1, fill="both", padx="30", pady="10")
        self.closeButton = tk.Button(master=self.dialog, text=buttonText, font=self.buttonFont, command=self.destroyDialog)
        self.closeButton.pack(expand=1, fill="both", padx="30", pady="10")

    def openResultDialog(self, displayText):
        self.openDialog(titleText="結果メッセージ")
        self.resultLabel = tk.Label(master=self.dialog, text=displayText, font=self.fontStyle)
        self.resultLabel.pack(expand=1)
        self.quitButton2 = tk.Button(master=self.dialog, text="プログラムを閉じる", font=self.buttonFont, command=sys.exit)
        self.quitButton2.pack(fill="both")
    
    def inputInfoDialog(self, titleText):
        self.textLabel["text"] = self.newWinMes
        self.dialog = tk.Toplevel(self)
        self.dialog.title(titleText)
        self.dialog.grab_set()
        self.errorMesPack()
        self.entryDays()
        self.buttonFrame = tk.Frame(master=self.dialog)
        self.buttonFrame.grid(row=3)
        self.checkButton = tk.Button(master=self.buttonFrame, text="入力チェック", font=self.buttonFont, command=self.valuecheck)
        self.commitButton = tk.Button(master=self.buttonFrame, text="登録", font=self.buttonFont, command=self.commitInput2DB, state=tk.DISABLED)
        self.quitButton = tk.Button(master=self.buttonFrame, text="キャンセルして終了", font=self.buttonFont, command=sys.exit)
        self.checkButton.pack(fill="both")
        self.commitButton.pack(fill="both")
        self.quitButton.pack(fill="both")
        
        return
    def errorMesPack(self):
        self.erMesFrame = tk.Frame(master=self.dialog)
        self.erMesFrame.grid(row=0)
        self.mesLabel = tk.Label(master=self.erMesFrame, text="カードを登録します。\nカードの所有者についての情報を入力してください。")
        self.errMes0 = tk.Label(self.erMesFrame, foreground="red")
        self.errMes1 = tk.Label(self.erMesFrame, foreground="red")
        self.errMes2 = tk.Label(self.erMesFrame, foreground="red")
        self.errMes3 = tk.Label(self.erMesFrame, foreground="red")
        self.mesLabel.pack()
        self.errMes0.pack()
        self.errMes1.pack()
        self.errMes2.pack()
        self.errMes3.pack()


    def entryDays(self):
        self.nameFrame = tk.LabelFrame(master=self.dialog, text="カードの所有者名", foreground="green")
        self.nameFrame.grid(row=1, padx=30)
        self.birthFrame = tk.LabelFrame(master=self.dialog, text="カード所有者の誕生日", foreground="green")
        self.birthFrame.grid(row=2, padx=30)
        self.nameEntry = tk.Entry(master=self.nameFrame, width=20)
        self.nameEntry.pack(fill="both")
        # 年 入力エントリー
        self.yearEntry = tk.Entry(master=self.birthFrame, width=4)
        self.yearEntry.pack(side=tk.LEFT)
        # 単位ラベル"年"
        self.yearLabel = tk.Label(master=self.birthFrame, text="年")
        self.yearLabel.pack(side=tk.LEFT)
        # 月 入力エントリー
        self.monthEntry = tk.Entry(master=self.birthFrame, width=2)
        self.monthEntry.pack(side=tk.LEFT)
        # 単位ラベル"月"
        self.monthLabel = tk.Label(master=self.birthFrame, text="月")
        self.monthLabel.pack(side=tk.LEFT)
        # 日 入力エントリー
        self.dayEntry = tk.Entry(master=self.birthFrame, width=2)
        self.dayEntry.pack(side=tk.LEFT)
        # 単位ラベル"日"
        self.dayLabel = tk.Label(master=self.birthFrame, text="日")
        self.dayLabel.pack(side=tk.LEFT)

    def valuecheck(self):
        self.allErrs = 0
        # 名前の入力を受け取る
        self.nameInput = self.nameEntry.get()
        intErrText = "には整数値を入力してください。"
        invalidErrText = "の値が不正です。値を確認してください。"

        # 入力文字列チェック 名前
        # インジェクション対策はAzure側でやる。
        if len(self.nameInput) == 0 or len(self.nameInput) >= 20:
            self.errMes0["text"] = "名前は1文字以上、20文字未満で入力してください。"
            self.allErrs += 1

        # 整数値チェック 年
        try:
            self.yearInput = int(self.yearEntry.get())
        except ValueError:
            self.errMes1["text"] = f"年{intErrText}"
            self.allErrs += 1
        else: # 値範囲チェック
            if self.yearInput < 0:
                # 細かい不正値はDB側のエラーでキャッチ
                self.errMes1["text"] = f"年{invalidErrText}"
                self.allErrs += 1
            else:
                self.errMes1["text"] = ""
        # 整数値チェック 月
        try:
            self.monthInput = int(self.monthEntry.get())
        except ValueError:
            self.errMes2["text"] = f"月{intErrText}"
            self.allErrs += 1
        else: # 値範囲チェック
            if self.monthInput <= 0 or self.monthInput > 12:
                self.errMes2["text"] = f"月{invalidErrText}"
                self.allErrs += 1
            else:
                self.errMes2["text"] = ""
        # 整数値チェック 日
        try:
            self.dayInput = int(self.dayEntry.get())
        except ValueError:
            self.errMes3["text"] = f"日{intErrText}"
            self.allErrs += 1
        else: # 値範囲チェック
            # 月や閏年に依存する部分の不正値はDB側のエラーでキャッチ
            if self.dayInput <= 0 or self.dayInput > 31:
                self.errMes3["text"] = f"日{invalidErrText}"
                self.allErrs += 1
            else:
                self.errMes3["text"] = ""
        # エラーの存在確認
        if self.allErrs != 0:
            return
        else:
            self.alterStateButtonEntry(option="check")

    def destroyDialog(self):
        self.textLabel = self.firstDispMes
        self.dialog.destroy()
        self.master.grab_set_global()
        self.startReadNfc()
    
    def alterStateButtonEntry(self, option):
        """
        Summary
        -------
        入力画面のボタンとエントリーの状態を
        オプションに応じて変える。
        check:
            登録/修正ボタンが押せるようになる
            チェックボタンとエントリーを反応しないようにする
        fix:
            checkの逆

        Parameters
        ----------
        option : str
            'checked' or 'fix'
        """
        if not option in ["check", "fix"]:
            return
        nor = [self.commitButton]
        dis = [self.nameEntry, self.yearEntry, self.monthEntry, self.dayEntry]
        if option == "check":
            for i in nor:
                i["state"] = tk.NORMAL
            for i in dis:
                i["state"] = tk.DISABLED
            self.checkButton["text"] = "修正"
            self.checkButton["command"] = lambda: self.alterStateButtonEntry(option="fix")
            return
        if option == "fix":
            for i in nor:
                i["state"] = tk.DISABLED
            for i in dis:
                i["state"] = tk.NORMAL
            self.checkButton["text"] = "入力チェック"
            self.checkButton["command"] = self.valuecheck
            return

        
    def commitInput2DB(self):
        birthday = f"{self.yearInput}-{self.monthInput}-{self.dayInput}"
        dataNow = datetime.datetime.now(tz=timezone('Asia/Tokyo'))
        tourokubi = f'{dataNow.year}-{dataNow.month:02d}-{dataNow.day:02d}'
        status_code = adnfc.add_crew(name=self.nameInput, birthday=birthday,\
                                    tourokubi=tourokubi, card_hash=self.cardID)
        if status_code == 200:
            self.dialog.destroy()
            mes = "カードの登録が成功しました。\n"
            mes += "このカードに特別な権限を設定したい場合は管理者に連絡してください。"
            self.openResultDialog(displayText=mes)
            return


        elif status_code == 400:
            mes = "入力された情報を登録できませんでした。次の点を確認してください。\n"
            mes += "・名前に特殊な文字を含んでいないか\n"
            mes += "・誕生日に存在しない日付を入力していないか"

        else:
            # 応答は200,400に設定しているので、この分岐は起こらないはずだが、念のため。
            mes = "予期せぬエラーが発生しました。\n"
            mes += "時間を置いて再試行してください。\n"
            mes += "それでも解決しない場合は管理者に問い合わせてください。"
        
        self.mesLabel["text"] = mes
        self.mesLabel["foreground"] = "red"
        return

def osIdentifier():
    osName = platform.system()
    if osName in ['Windows', 'Darwin', 'Linux']:
        return osName
    else:
        return None

def overrider(winObj):
    osName = osIdentifier()
    if osName in ['Linux', 'Darwin']:
        return
    else:
        winObj.overrideredirect(True)


def zoomer(winObj):
    """
    OSごとの処理の違いを吸収して画面をフルスクリーン化する
    """
    osName = osIdentifier()
    if osName in ['Linux', 'Darwin']:
        winObj.attributes('-fullscreen', True)
    elif osName == 'Windows':
        winObj.state('zoomed')
        overrider(winObj=winObj)
        return


root = tk.Tk()
root.title('カード新規登録')

zoomer(root)

app = Application(master=root)
app.mainloop()