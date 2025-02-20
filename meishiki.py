import sys
from datetime import datetime, timedelta

import kanshi_data as kd


class Meishiki:
    """
    命式のクラス
    """

    def __init__(self, birthday, t_flag, sex):

        self.birthday = birthday
        self.t_flag = t_flag
        self.sex = sex
        self.meishiki = {}

    def is_setsuiri(self, birthday, month):
        """
        ＜機能＞
        birthday の年月日が、month で与えられた月に対して節入りしているか否かを判定する
        ＜入力＞
        - birthday（datetime）：誕生日
        - month（int）：基準となる月
        ＜出力＞
        - 節入りしている（0）またはしていない（-1）の二値
        ＜異常検出＞
        判定不可能の場合はエラーメッセージを出力して強制終了する
        """

        for s in kd.setsuiri:
            if (s[0] == birthday.year) and (s[1] == month):
                setsuiri = datetime(year=s[0], month=s[1], day=s[2],
                                    hour=s[3], minute=s[4])
                if setsuiri < birthday:
                    return 0    # 節入りしている

                return -1   # 節入りしていない

        print('節入りを判定できませんでした。')
        sys.exit(1)

    def find_year_kanshi(self, birthday):
        """
        ＜機能＞
        birthday の生年月日の年干支を取得する
        ＜入力＞
            - birthday（datetime）：誕生日
        ＜出力＞
            - y_kan（int）：年干の番号
            - y_shi（int）：年支の番号
        ＜異常検出＞
        取得できなかった場合はエラーメッセージを出力して強制終了する
        """

        sixty_kanshi_idx = \
            (birthday.year - 3) % 60 - 1 + self.is_setsuiri(birthday, 2)
        try:
            y_kan, y_shi = kd.sixty_kanshi[sixty_kanshi_idx]
            return y_kan, y_shi
        except IndexError:
            print('年干支の計算で例外が送出されました。')
            sys.exit(1)

    def find_month_kanshi(self, birthday, y_kan):
        """
        ＜機能＞
        birthday の生年月日の月干支を取得する
        ＜入力＞
          - birthday（datetime）：誕生日
          - y_kan（int）：年干の番号
        ＜出力＞
          - m_kan（int）：月干の番号
          - m_shi（int）：月支の番号
        ＜異常検出＞
        取得できなかった場合はエラーメッセージを出力して強制終了する
        """

        month = birthday.month - 1 + self.is_setsuiri(birthday, birthday.month)
        try:
            m_kan, m_shi = kd.month_kanshi[y_kan][month]
            return m_kan, m_shi
        except IndexError:
            print('月干支の計算で例外が送出されました。')
            sys.exit(1)

    def find_day_kanshi(self, birthday):
        """
        ＜機能＞
        birthday で与えられた生年月日の日干支を取得する
        ＜入力＞
          - birthday（daytime）：誕生日
        ＜出力＞
          - d_kan（int）：日干の番号
          - d_shi（int）：日支の番号
        ＜異常検出＞
        取得できなかった場合はエラーメッセージを出力して強制終了する
        """
        try:
            d = birthday.day + \
                kd.kisu_table[birthday.year - 1926][birthday.month - 1] - 1
        except IndexError:
            print('生年は1926年以降でなければなりません。')
            sys.exit(1)

        if d >= 60:
            d -= 60  # d が 60 を超えたら 60 を引く

        try:
            d_kan, d_shi = kd.sixty_kanshi[d]
            return d_kan, d_shi
        except IndexError:
            print('日干支の計算で例外が送出されました。')
            sys.exit(1)

    def find_time_kanshi(self, birthday, d_kan):
        """
        ＜機能＞
        birthday で与えられた生年月日の時干支を取得する
        ＜入力＞
          - birthday（datetime）：誕生日
          - d_kan（int）：日干の番号
        ＜出力＞
          - t_kan（int）：時干の番号
          - t_shi（int）：時支の番号
        ＜異常検出＞
        取得できなかった場合はエラーメッセージを出力して強制終了する
        """
        time_span = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 24]

        for i in range(len(time_span) - 1):

            from_dt = datetime(year=birthday.year,
                               month=birthday.month,
                               day=birthday.day,
                               hour=time_span[i],
                               minute=0)

            if (i == 0) or (i == len(time_span)):
                to_dt = from_dt + timedelta(hours=0, minutes=59)
            else:
                to_dt = from_dt + timedelta(hours=1, minutes=59)

            if from_dt <= birthday <= to_dt:
                try:
                    t_kan, t_shi = kd.time_kanshi[d_kan][i]
                    return t_kan, t_shi
                except IndexError:
                    print('時干支の計算で例外が送出されました。')
                    sys.exit(1)

        print('時干支を得られませんでした。')
        sys.exit(1)

    def find_zokan(self, birthday, shi):
        """
        ＜機能＞
        birthday で与えられた生年月日の shi に対応する蔵干を取得する
        ＜入力＞
          - birthday（datetime）：誕生日
          - shi（int）：年支、月支、日支、時支の番号
        ＜出力＞
          - z_kan（int）：蔵干の番号
        ＜異常検出＞
        取得できなかった場合はエラーメッセージを出力して強制終了する
        """

        # 直近の節入り日時を取得する
        p = self.is_setsuiri(birthday, birthday.month)
        for s in kd.setsuiri:
            if (s[0] == birthday.year) and (s[1] == birthday.month):
                if s[1] + p <= 0:
                    y = s[0] - 1
                    m = 12
                else:
                    y = s[0]
                    m = s[1] + p
                setsuiri = datetime(year=y, month=m, day=s[2],
                                    hour=s[3], minute=s[4])

        # 蔵干が「午」の場合は例外
        if shi == 6:
            delta1 = timedelta(
                days=kd.zokan_time[6][0][0], hours=kd.zokan_time[6][0][1])
            delta2 = timedelta(
                days=kd.zokan_time[6][1][0], hours=kd.zokan_time[6][1][1])
        else:
            delta = timedelta(
                days=kd.zokan_time[shi][0], hours=kd.zokan_time[shi][1])

        try:
            if shi == 6:
                if setsuiri + delta1 >= birthday:
                    zokan = kd.zokan[6][0]
                elif setsuiri + delta1 < birthday <= setsuiri + delta2:
                    zokan = kd.zokan[6][1]
                else:
                    zokan = kd.zokan[6][2]
            else:
                if setsuiri + delta >= birthday:
                    zokan = kd.zokan[shi][0]
                else:
                    zokan = kd.zokan[shi][1]
            return zokan
        except IndexError:
            print('蔵干の計算で例外が送出されました。')
            sys.exit(1)

    def append_gogyo(self, tenkan, chishi):
        """
        五行（木火土金水）のそれぞれの数を得る
        """
        gogyo = [0] * 5
        try:
            for t in tenkan:
                if t != -1:
                    gogyo[kd.gogyo_kan[t]] += 1
        except IndexError:
            print('五行の計算で例外が送出されました。')
            sys.exit(1)
        try:
            for c in chishi:
                if c != -1:
                    gogyo[kd.gogyo_shi[c]] += 1
        except IndexError:
            print('五行の計算で例外が送出されました。')
            sys.exit(1)

        return gogyo

    def append_inyo(self, tenkan, chishi):
        """
        陰陽のそれぞれの数を得る
        """
        inyo = [0] * 2
        for k in tenkan:
            inyo[k % 2] += 1
        for s in chishi:
            inyo[s % 2] += 1
        return inyo

    def append_getsurei(self, d_kan, m_shi):
        """
        月令を得る
        """
        if m_shi in kd.getsurei_ou[d_kan]:
            return 1
        if m_shi in kd.getsurei_sou[d_kan]:
            return 2
        return 0

    def append_tsuhen(self, tenkan, zokan):
        """
        通変を得る
        """
        tsuhen = []
        try:
            for i in tenkan + zokan:
                if i == -1:
                    tsuhen.append(-1)
                else:
                    tsuhen.append(kd.kan_tsuhen[tenkan[2]].index(i))
        except IndexError:
            print('通変の計算で例外が送出されました。')
            sys.exit(1)

        return tsuhen

    def append_twelve_fortune(self, tenkan, chishi):
        """
        十二運を得る
        """
        twelve_fortune = []
        try:
            for c in chishi:
                if c == -1:
                    twelve_fortune.append(-1)
                else:
                    twelve_fortune.append(kd.twelve_table[tenkan[2]][c])
        except IndexError:
            print('十二運の計算で例外が送出されました。')
            sys.exit(1)

        return twelve_fortune

    def append_kango(self, tenkan_zokan):
        """
        ＜機能＞
        干合を命式に追加する
        ＜入力＞
          - 天干＋蔵干
        ＜出力＞
          - 干合のリスト
            [[干合する干１, 干１の場所（0〜7）], [干合する干２, 干２の場所], 変化する五行]
        """
        kango = []
        for i, tz1 in enumerate(tenkan_zokan):
            if tz1 == -1:
                continue
            for j in list(range(i, len(tenkan_zokan))):
                if kd.kango[tz1] == tenkan_zokan[j] and i != j:
                    kango.append(
                        [[tz1, i], [tenkan_zokan[j], j], kd.kango_henka[tz1]])
        return kango

    def append_shigo(self, chishi):
        """
        ＜機能＞
        支合を命式に追加する
        ＜入力＞
          - 地支
        ＜出力＞
          - 支合のリスト
            [[支合する支１, 支１の場所（0〜3）], [支合する支２, 支２の場所]]
        """
        shigo = []
        for i, s in enumerate(chishi):
            if s == -1:
                continue
            for j in list(range(i, len(chishi))):
                if kd.shigo[s] == chishi[j] and i != j:
                    shigo.append([[s, i], [kd.shigo[s], j]])
        return shigo

    def append_hogo(self, chishi):
        """
        ＜機能＞
        方合を命式に追加する
        ＜入力＞
          - 地支
        ＜出力＞
          - 方合のリスト
        """
        for i, h in enumerate(kd.hogo):
            if (h[0][0] in chishi) and (h[0][1] in chishi) and (h[0][2] in chishi):
                return kd.hogo[i]
        return []

    def append_sango(self, chishi):
        """
        ＜機能＞
        三合を命式に追加する
        ＜入力＞
          - 地支
        ＜出力＞
          - 三合のリスト
        """
        for i, s in enumerate(kd.sango):
            if (s[0][0] in chishi) and (s[0][1] in chishi) and (s[0][2] in chishi):
                return kd.sango[i]
        return []

    def append_hankai(self, chishi):
        """
        ＜機能＞
        半会を命式に追加する
        ＜入力＞
          - 地支
        ＜出力＞
          - 半会のリスト
        """
        hankai = []
        for h in kd.hankai:
            if (h[0][0] in chishi) and (h[0][1] in chishi):
                hankai.append(h)
        return hankai

    def append_hitsuchu(self, chishi):
        """
        ＜機能＞
        七冲を命式に追加する
        ＜入力＞
          - 地支
        ＜出力＞
          - 七冲のリスト
        """
        hitsuchu = []
        for i, s in enumerate(chishi):
            if s == -1:
                continue
            for j in list(range(i, len(chishi))):
                if kd.hitsuchu[s] == chishi[j] and i != j:
                    hitsuchu.append([[s, i], [kd.hitsuchu[s], j]])
        return hitsuchu

    def append_kei(self, chishi):
        """
        ＜機能＞
        刑を命式に追加する
        ＜入力＞
          - 地支
        ＜出力＞
          - 刑のリスト
        """
        kei = []
        for i, s in enumerate(chishi):
            if s == -1:
                continue
            for j in list(range(0, len(chishi))):
                if kd.kei[s] == chishi[j] and i != j:
                    kei.append([[s, i], [kd.kei[s], j]])
        return kei

    def append_gai(self, chishi):
        """
        ＜機能＞
        害を命式に追加する
        ＜入力＞
          - 地支
        ＜出力＞
          - 害のリスト
        """
        gai = []
        for i, s in enumerate(chishi):
            if s == -1:
                continue
            for j in list(range(i, len(chishi))):
                if kd.gai[s] == chishi[j] and i != j:
                    gai.append([[s, i], [kd.gai[s], j]])
        return gai

    def append_choko(self, birthday, d_kan):
        """
        調候を得る
        """
        try:
            choko = kd.choko[d_kan][birthday.month - 1]
        except IndexError:
            print('調候の計算で例外が送出されました。')
            sys.exit(1)

        return choko

    def append_kubo(self, birthday):
        """
        空亡を得る
        """
        try:
            d = birthday.day + \
                kd.kisu_table[(birthday.year - 1926) %
                              80][birthday.month - 1] - 1
            if d >= 60:
                d -= 60  # d が 60 を超えたら 60 を引く
            kubo = kd.kubo[d // 10]
        except IndexError:
            print('空亡の計算で例外が送出されました。')
            sys.exit(1)

        return kubo

    def append_youjin(self, d_kan, d_shi):
        """
        陽刃を得る
        """
        if d_kan == 2 and d_shi == 6:    # 丙午
            return 1
        elif d_kan == 4 and d_shi == 6:  # 戊午
            return 1
        elif d_kan == 8 and d_shi == 0:  # 壬子
            return 1
        else:
            return 0

    def append_kaigou(self, d_kan, d_shi):
        """
        魁罡を得る
        """
        if d_kan == 4 and d_shi == 10:   # 戊戌
            return 1
        elif d_kan == 6 and d_shi == 10:  # 庚戌
            return 1
        elif d_kan == 6 and d_shi == 4:  # 庚辰
            return 1
        elif d_kan == 8 and d_shi == 4:  # 壬辰
            return 1
        else:
            return 0

    def build_meishiki(self):
        """
        命式を組成する
        """

        # 天干・地支を得る
        y_kan, y_shi = self.find_year_kanshi(self.birthday)
        m_kan, m_shi = self.find_month_kanshi(self.birthday, y_kan)
        d_kan, d_shi = self.find_day_kanshi(self.birthday)
        if self.t_flag:
            t_kan, t_shi = self.find_time_kanshi(self.birthday, d_kan)
        else:
            t_kan = -1
            t_shi = -1

        # 蔵干を得る
        y_zkan = self.find_zokan(self.birthday, y_shi)
        m_zkan = self.find_zokan(self.birthday, m_shi)
        d_zkan = self.find_zokan(self.birthday, d_shi)
        if self.t_flag:
            t_zkan = self.find_zokan(self.birthday, t_shi)
        else:
            t_zkan = -1

        tenkan = [y_kan, m_kan, d_kan, t_kan]
        chishi = [y_shi, m_shi, d_shi, t_shi]
        zokan = [y_zkan, m_zkan, d_zkan, t_zkan]

        nenchu = [y_kan, y_shi, y_zkan]
        getchu = [m_kan, m_shi, m_zkan]
        nitchu = [d_kan, d_shi, d_zkan]
        jichu = [t_kan, t_shi, t_zkan]
        nikkan = d_kan

        # 五行（木火土金水）のそれぞれの数を得る
        gogyo = self.append_gogyo(tenkan, chishi)

        # 陰陽のそれぞれの数を得る
        inyo = self.append_inyo(tenkan, chishi)

        # 月令を得る
        getsurei = self.append_getsurei(d_kan, m_shi)

        # 通変を得る
        tsuhen = self.append_tsuhen(tenkan, zokan)

        # 十二運を得る
        twelve_fortune = self.append_twelve_fortune(tenkan, chishi)

        # 干合を得る
        kango = self.append_kango(tenkan + zokan)

        # 支合を得る
        shigo = self.append_shigo(chishi)

        # 方合・三合・半会を得る
        hogo = self.append_hogo(chishi)
        sango = self.append_sango(chishi)
        if not sango:
            hankai = self.append_hankai(chishi)
        else:
            hankai = []

        # 七冲・刑・害を得る
        hitsuchu = self.append_hitsuchu(chishi)
        kei = self.append_kei(chishi)
        gai = self.append_gai(chishi)

        # 調候を得る
        choko = self.append_choko(self.birthday, d_kan)

        # 空亡を得る
        kubo = self.append_kubo(self.birthday)

        # 陽刃・魁罡を得る
        youjin = self.append_youjin(d_kan, d_shi)
        kaigou = self.append_kaigou(d_kan, d_shi)

        # クラス変数 meishiki に情報を追加する
        self.meishiki.update({"tenkan": tenkan})
        self.meishiki.update({"chishi": chishi})
        self.meishiki.update({"zokan": zokan})
        self.meishiki.update({"nenchu": nenchu})
        self.meishiki.update({"getchu": getchu})
        self.meishiki.update({"nitchu": nitchu})
        self.meishiki.update({"jichu": jichu})
        self.meishiki.update({"nikkan": nikkan})
        self.meishiki.update({"gogyo": gogyo})
        self.meishiki.update({"inyo": inyo})
        self.meishiki.update({"getsurei": getsurei})
        self.meishiki.update({"tsuhen": tsuhen})
        self.meishiki.update({"twelve_fortune": twelve_fortune})
        self.meishiki.update({"kango": kango})
        self.meishiki.update({"shigo": shigo})
        self.meishiki.update({"hogo": hogo})
        self.meishiki.update({"sango": sango})
        self.meishiki.update({"hankai": hankai})
        self.meishiki.update({"hitsuchu": hitsuchu})
        self.meishiki.update({"kei": kei})
        self.meishiki.update({"gai": gai})
        self.meishiki.update({"choko": choko})
        self.meishiki.update({"kubo": kubo})
        self.meishiki.update({"youjin": youjin})
        self.meishiki.update({"kaigou": kaigou})