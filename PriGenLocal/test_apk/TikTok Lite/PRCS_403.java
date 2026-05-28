/*Application Package Name: com.tiktok.lite.go
class PRCS_403 {
/**
X.40e;L(Ljava/lang/String; Lorg/json/JSONObject;)V
*/

    public static void L(String p22, org.json.JSONObject p23)
    {
        try {
            android.accounts.Account[] v14_1;
            android.accounts.AccountManager v9 = android.accounts.AccountManager.get(X.16B.LB);
            com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            int v0_1 = 1;
            Object[] v10 = new Object[1];
            v10[0] = "com.google";
            com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;)[Landroid/accounts/Account;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOurYJDb0ibEEftgpwxkw68pqpAxGKmGaTKGsgU6I5UdbinR");
            org.json.JSONObject v2_0 = v4_1.preInvoke(102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, "android.accounts.Account[]", v11_1);
        } catch (Exception) {
            return;
        }
        if (!v2_0.intercept) {
            v14_1 = v9.getAccountsByType("com.google");
            v4_1.postInvoke(v14_1, 102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, v11_1, 1);
        } else {
            v4_1.postInvoke(0, 102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, v11_1, 0);
            v14_1 = ((android.accounts.Account[]) v2_0.returnValue);
        }
        if ((v14_1.length == 0) || (!kotlin.jvm.internal.Intrinsics.L(p22, v14_1[0].name))) {
            v0_1 = 0;
        }
        X.4FU.L("login_params_check", v0_1, p23);
        return;
    }

/**
X.5P9;onClick$36(LX/5P9; Landroid/view/View;)V
*/

    public static final void onClick$36(X.5P9 p6, android.view.View p7)
    {
        X.42S v4_1 = ((X.42f) p6.l0);
        String v5_1 = new org.json.JSONObject();
        v5_1.put("platform", "email");
        v5_1.put("enter_method", v4_1.LICI());
        v5_1.put("stay_time", (System.currentTimeMillis() - v4_1.L));
        if (X.7EA.LB()) {
            X.5PY v1_0;
            if (!v4_1.LB) {
                v1_0 = "unchecked";
            } else {
                v1_0 = "checked";
            }
            v5_1.put("email_checkbox_status", v1_0);
        }
        X.4br.L("register_click_next", v5_1);
        X.40e.L(((X.46A) v4_1._$_findCachedViewById(2131297141)).L(), new X.4D8().LB());
        X.42f v6_2 = ((X.42f) p6.l0);
        X.44N v2_2 = ((X.46A) v6_2._$_findCachedViewById(2131297141)).L();
        if ((android.text.TextUtils.isEmpty(v2_2)) || (!android.util.Patterns.EMAIL_ADDRESS.matcher(v2_2).matches())) {
            v6_2.L(0, v6_2.getString(2131755844));
            X.42b.L(0, v6_2.LICI());
            return;
        } else {
            ((X.44u) v6_2._$_findCachedViewById(2131297142)).L();
            X.44k.L(v6_2, new X.44N(v6_2, new X.5PU(v6_2, 29), X.42S.SIGN_UP, v6_2.LFI()), new X.5PY(v6_2, ((X.46A) v6_2._$_findCachedViewById(2131297141)).L(), 2));
            return;
        }
    }

/**
X.5P9;onClick(Landroid/view/View;)V
*/

    public final void onClick(android.view.View p2)
    {
        switch (this.$t) {
            case 0:
                X.5P9.onClick$0(((X.5P9) this), p2);
                return;
            case 1:
                X.5P9.onClick$1(((X.5P9) this), p2);
                return;
            case 2:
                X.5P9.onClick$2(((X.5P9) this), p2);
                return;
            case 3:
                X.5P9.onClick$3(((X.5P9) this), p2);
                return;
            case 4:
                X.5P9.onClick$4(((X.5P9) this), p2);
                return;
            case 5:
                X.5P9.onClick$5(((X.5P9) this), p2);
                return;
            case 6:
                X.5P9.onClick$6(((X.5P9) this), p2);
                return;
            case 7:
                X.5P9.onClick$7(((X.5P9) this), p2);
                return;
            case 8:
                X.5P9.onClick$8(((X.5P9) this), p2);
                return;
            case 9:
                X.5P9.onClick$9(((X.5P9) this), p2);
                return;
            case 10:
                X.5P9.onClick$10(((X.5P9) this), p2);
                return;
            case 11:
                X.5P9.onClick$11(((X.5P9) this), p2);
                return;
            case 12:
                X.5P9.onClick$12(((X.5P9) this), p2);
                return;
            case 13:
                X.5P9.onClick$13(((X.5P9) this), p2);
                return;
            case 14:
                X.5P9.onClick$14(((X.5P9) this), p2);
                return;
            case 15:
                X.5P9.onClick$15(((X.5P9) this), p2);
                return;
            case 16:
                X.5P9.onClick$16(((X.5P9) this), p2);
                return;
            case 17:
                X.5P9.onClick$17(((X.5P9) this), p2);
                return;
            case 18:
                X.5P9.onClick$18(((X.5P9) this), p2);
                return;
            case 19:
                X.5P9.onClick$19(((X.5P9) this), p2);
                return;
            case 20:
                X.5P9.onClick$20(((X.5P9) this), p2);
                return;
            case 21:
                X.5P9.onClick$21(((X.5P9) this), p2);
                return;
            case 22:
                X.5P9.onClick$22(((X.5P9) this), p2);
                return;
            case 23:
                X.5P9.onClick$23(((X.5P9) this), p2);
                return;
            case 24:
                X.5P9.onClick$24(((X.5P9) this), p2);
                return;
            case 25:
                X.5P9.onClick$25(((X.5P9) this), p2);
                return;
            case 26:
                X.5P9.onClick$26(((X.5P9) this), p2);
                return;
            case 27:
                X.5P9.onClick$27(((X.5P9) this), p2);
                return;
            case 28:
                X.5P9.onClick$28(((X.5P9) this), p2);
                return;
            case 29:
                X.5P9.onClick$29(((X.5P9) this), p2);
                return;
            case 30:
                X.5P9.onClick$30(((X.5P9) this), p2);
                return;
            case 31:
                X.5P9.onClick$31(((X.5P9) this), p2);
                return;
            case 32:
                X.5P9.onClick$32(((X.5P9) this), p2);
                return;
            case 33:
                X.5P9.onClick$33(((X.5P9) this), p2);
                return;
            case 34:
                X.5P9.onClick$34(((X.5P9) this), p2);
                return;
            case 35:
                X.5P9.onClick$35(((X.5P9) this), p2);
                return;
            case 36:
                X.5P9.onClick$36(((X.5P9) this), p2);
                return;
            case 37:
                X.5P9.onClick$37(((X.5P9) this), p2);
                return;
            case 38:
                X.5P9.onClick$38(((X.5P9) this), p2);
                return;
            case 39:
                X.5P9.onClick$39(((X.5P9) this), p2);
                return;
            case 40:
                X.5P9.onClick$40(((X.5P9) this), p2);
                return;
            case 41:
                X.5P9.onClick$41(((X.5P9) this), p2);
                return;
            case 42:
                X.5P9.onClick$42(((X.5P9) this), p2);
                return;
            case 43:
                X.5P9.onClick$43(((X.5P9) this), p2);
                return;
            case 44:
                X.5P9.onClick$44(((X.5P9) this), p2);
                return;
            case 45:
                X.5P9.onClick$45(((X.5P9) this), p2);
                return;
            case 46:
                X.5P9.onClick$46(((X.5P9) this), p2);
                return;
            case 47:
                X.5P9.onClick$47(((X.5P9) this), p2);
                return;
            case 48:
                X.5P9.onClick$48(((X.5P9) this), p2);
                return;
            case 49:
                X.5P9.onClick$49(((X.5P9) this), p2);
                return;
            case 50:
                X.5P9.onClick$50(((X.5P9) this), p2);
                return;
            case 51:
                X.5P9.onClick$51(((X.5P9) this), p2);
                return;
            case 52:
                X.5P9.onClick$52(((X.5P9) this), p2);
                return;
            case 53:
                X.5P9.onClick$53(((X.5P9) this), p2);
                return;
            case 54:
                X.5P9.onClick$54(((X.5P9) this), p2);
                return;
            case 55:
                X.5P9.onClick$55(((X.5P9) this), p2);
                return;
            case 56:
                X.5P9.onClick$56(((X.5P9) this), p2);
                return;
            case 57:
                X.5P9.onClick$57(((X.5P9) this), p2);
                return;
            case 58:
                X.5P9.onClick$58(((X.5P9) this), p2);
                return;
            case 59:
                X.5P9.onClick$59(((X.5P9) this), p2);
                return;
            case 60:
                X.5P9.onClick$60(((X.5P9) this), p2);
                return;
            case 61:
                X.5P9.onClick$61(((X.5P9) this), p2);
                return;
            case 62:
                X.5P9.onClick$62(((X.5P9) this), p2);
                return;
            case 63:
                X.5P9.onClick$63(((X.5P9) this), p2);
                return;
            case 64:
                X.5P9.onClick$64(((X.5P9) this), p2);
                return;
            case 65:
                X.5P9.onClick$65(((X.5P9) this), p2);
                return;
            case 66:
                X.5P9.onClick$66(((X.5P9) this), p2);
                return;
            case 67:
                X.5P9.onClick$67(((X.5P9) this), p2);
                return;
            case 68:
                X.5P9.onClick$68(((X.5P9) this), p2);
                return;
            case 69:
                X.5P9.onClick$69(((X.5P9) this), p2);
                return;
            case 70:
                X.5P9.onClick$70(((X.5P9) this), p2);
                return;
            case 71:
                X.5P9.onClick$71(((X.5P9) this), p2);
                return;
            case 72:
                X.5P9.onClick$72(((X.5P9) this), p2);
                return;
            case 73:
                X.5P9.onClick$73(((X.5P9) this), p2);
                return;
            case 74:
                X.5P9.onClick$74(((X.5P9) this), p2);
                return;
            case 75:
                X.5P9.onClick$75(((X.5P9) this), p2);
                return;
            case 76:
                X.5P9.onClick$76(((X.5P9) this), p2);
                return;
            case 77:
                X.5P9.onClick$77(((X.5P9) this), p2);
                return;
            case 78:
                X.5P9.onClick$78(((X.5P9) this), p2);
                return;
            case 79:
                X.5P9.onClick$79(((X.5P9) this), p2);
                return;
            case 80:
                X.5P9.onClick$80(((X.5P9) this), p2);
                return;
            case 81:
                X.5P9.onClick$81(((X.5P9) this), p2);
                return;
            case 82:
                X.5P9.onClick$82(((X.5P9) this), p2);
                return;
            case 83:
                X.5P9.onClick$83(((X.5P9) this), p2);
                return;
            case 84:
                X.5P9.onClick$84(((X.5P9) this), p2);
                return;
            case 85:
                X.5P9.onClick$85(((X.5P9) this), p2);
                return;
            case 86:
                X.5P9.onClick$86(((X.5P9) this), p2);
                return;
            case 87:
                X.5P9.onClick$87(((X.5P9) this), p2);
                return;
            case 88:
                X.5P9.onClick$88(((X.5P9) this), p2);
                return;
            case 89:
                X.5P9.onClick$89(((X.5P9) this), p2);
                return;
            case 90:
                X.5P9.onClick$90(((X.5P9) this), p2);
                return;
            case 91:
                X.5P9.onClick$91(((X.5P9) this), p2);
                return;
            case 92:
                X.5P9.onClick$92(((X.5P9) this), p2);
                return;
            case 93:
                X.5P9.onClick$93(((X.5P9) this), p2);
                return;
            case 94:
                X.5P9.onClick$94(((X.5P9) this), p2);
                return;
            case 95:
                X.5P9.onClick$95(((X.5P9) this), p2);
                return;
            case 96:
                X.5P9.onClick$96(((X.5P9) this), p2);
                return;
            case 97:
                X.5P9.onClick$97(((X.5P9) this), p2);
                return;
            case 98:
                X.5P9.onClick$98(((X.5P9) this), p2);
                return;
            case 99:
                X.5P9.onClick$99(((X.5P9) this), p2);
                return;
            case 100:
                X.5P9.onClick$100(((X.5P9) this), p2);
                return;
            case 101:
                X.5P9.onClick$101(((X.5P9) this), p2);
                return;
            case 102:
                X.5P9.onClick$102(((X.5P9) this), p2);
                return;
            case 103:
                X.5P9.onClick$103(((X.5P9) this), p2);
                return;
            case 104:
                X.5P9.onClick$104(((X.5P9) this), p2);
                return;
            case 105:
                X.5P9.onClick$105(((X.5P9) this), p2);
                return;
            case 106:
                X.5P9.onClick$106(((X.5P9) this), p2);
                return;
            case 107:
                X.5P9.onClick$107(((X.5P9) this), p2);
                return;
            case 108:
                X.5P9.onClick$108(((X.5P9) this), p2);
                return;
            case 109:
                X.5P9.onClick$109(((X.5P9) this), p2);
                return;
            case 110:
                X.5P9.onClick$110(((X.5P9) this), p2);
                return;
            case 111:
                X.5P9.onClick$111(((X.5P9) this), p2);
                return;
            case 112:
                X.5P9.onClick$112(((X.5P9) this), p2);
                return;
            case 113:
                X.5P9.onClick$113(((X.5P9) this), p2);
                return;
            case 114:
                X.5P9.onClick$114(((X.5P9) this), p2);
                return;
            case 115:
                X.5P9.onClick$115(((X.5P9) this), p2);
                return;
            case 116:
                X.5P9.onClick$116(((X.5P9) this), p2);
                return;
            case 117:
                X.5P9.onClick$117(((X.5P9) this), p2);
                return;
            case 118:
                X.5P9.onClick$118(((X.5P9) this), p2);
                return;
            case 119:
                X.5P9.onClick$119(((X.5P9) this), p2);
                return;
            case 120:
                X.5P9.onClick$120(((X.5P9) this), p2);
                return;
            case 121:
                X.5P9.onClick$121(((X.5P9) this), p2);
                return;
            case 122:
                X.5P9.onClick$122(((X.5P9) this), p2);
                return;
            case 123:
                X.5P9.onClick$123(((X.5P9) this), p2);
                return;
            case 124:
                X.5P9.onClick$124(((X.5P9) this), p2);
                return;
            case 125:
                X.5P9.onClick$125(((X.5P9) this), p2);
                return;
            case 126:
                X.5P9.onClick$126(((X.5P9) this), p2);
                return;
            case 127:
                X.5P9.onClick$127(((X.5P9) this), p2);
                return;
            case 128:
                X.5P9.onClick$128(((X.5P9) this), p2);
                return;
            case 129:
                X.5P9.onClick$129(((X.5P9) this), p2);
                return;
            case 130:
                X.5P9.onClick$130(((X.5P9) this), p2);
                return;
            case 131:
                X.5P9.onClick$131(((X.5P9) this), p2);
                return;
            case 132:
                X.5P9.onClick$132(((X.5P9) this), p2);
                return;
            case 133:
                X.5P9.onClick$133(((X.5P9) this), p2);
                return;
            case 134:
                X.5P9.onClick$134(((X.5P9) this), p2);
                return;
            case 135:
                X.5P9.onClick$135(((X.5P9) this), p2);
                return;
            case 136:
                X.5P9.onClick$136(((X.5P9) this), p2);
                return;
            case 137:
                X.5P9.onClick$137(((X.5P9) this), p2);
                return;
            case 138:
                X.5P9.onClick$138(((X.5P9) this), p2);
                return;
            case 139:
                X.5P9.onClick$139(((X.5P9) this), p2);
                return;
            case 140:
                X.5P9.onClick$140(((X.5P9) this), p2);
                return;
            case 141:
                X.5P9.onClick$141(((X.5P9) this), p2);
                return;
            case 142:
                X.5P9.onClick$142(((X.5P9) this), p2);
                return;
            case 143:
                X.5P9.onClick$143(((X.5P9) this), p2);
                return;
            case 144:
                X.5P9.onClick$144(((X.5P9) this), p2);
                return;
            case 145:
                X.5P9.onClick$145(((X.5P9) this), p2);
                return;
            case 146:
                X.5P9.onClick$146(((X.5P9) this), p2);
                return;
            case 147:
                X.5P9.onClick$147(((X.5P9) this), p2);
                return;
            case 148:
                X.5P9.onClick$148(((X.5P9) this), p2);
                return;
            case 149:
                X.5P9.onClick$149(((X.5P9) this), p2);
                return;
            case 150:
                X.5P9.onClick$150(((X.5P9) this), p2);
                return;
            case 151:
                X.5P9.onClick$151(((X.5P9) this), p2);
                return;
            case 152:
                X.5P9.onClick$152(((X.5P9) this), p2);
                return;
            case 153:
                X.5P9.onClick$153(((X.5P9) this), p2);
                return;
            case 154:
                X.5P9.onClick$154(((X.5P9) this), p2);
                return;
            case 155:
                X.5P9.onClick$155(((X.5P9) this), p2);
                return;
            case 156:
                X.5P9.onClick$156(((X.5P9) this), p2);
                return;
            default:
                return;
        }
    }


}