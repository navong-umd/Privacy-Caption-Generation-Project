/*Application Package Name: com.tiktok.lite.go
class PRCS_326 {
/**
Y.ACallableS4S0200000_2;L$0(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L$0(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOepapGA1D2uHixzf4/2/eF4ePVa5xI71fNFx86TMohshC31S/4F9UkO/g4d5PArxljOCGSLpQcvLcWRG9n0dH+ZomKipg==");
            com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, "android.net.NetworkInfo", v10_1);
        } catch (android.net.NetworkInfo v0_3) {
            v0_3.printStackTrace();
            return X.1Mw.L();
        }
        if (!v1_0.intercept) {
            android.net.NetworkInfo v4_0 = p18.getActiveNetworkInfo();
            v3_1.postInvoke(v4_0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 1);
            return v4_0;
        } else {
            v3_1.postInvoke(0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 0);
            return ((android.net.NetworkInfo) v1_0.returnValue);
        }
    }

/**
Y.ACallableS4S0200000_2;call$10(LY/ACallableS4S0200000_2;)Ljava/lang/Object;
*/

    public static final synthetic Object call$10(Y.ACallableS4S0200000_2 p19)
    {
        String v0_4;
        String v1_2;
        int v3_1 = new X.4DB();
        v3_1.L("enter_from", ((X.6uW) p19.l0).LIILLL.L);
        v3_1.L("enter_method", "video_play");
        v3_1.L("airplane_mode_is_on", X.76h.L(((android.content.Context) p19.l1)));
        X.4br.L("no_internet_connection_page_show", v3_1.L);
        String v1_10 = ((android.content.Context) p19.l1).getSystemService("wifi");
        java.util.Objects.requireNonNull(v1_10, "null cannot be cast to non-null type android.net.wifi.WifiManager");
        if (!((android.net.wifi.WifiManager) v1_10).isWifiEnabled()) {
            int v3_2 = ((android.content.Context) p19.l1).getSystemService("connectivity");
            if ((v3_2 != 0) && ((v3_2 instanceof android.net.ConnectivityManager))) {
                int v3_3 = ((android.net.ConnectivityManager) v3_2);
                try {
                    android.net.NetworkInfo v9;
                    System.nanoTime();
                } catch (String v0_35) {
                    X.5If.L(v0_35);
                    v9 = Y.ACallableS4S0200000_2.L$0(v3_3);
                    v0_4 = new X.4DB();
                    if (v9 != null) {
                        com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v10 = new Object[0];
                        com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOepapGA1D2uHixzf4/2/eF4ePVa5xI71fNFx86TMohshC31S/4F9UkO/g4d5PArxljOCGSLpQcvLcWRG9n0dH+ZomKipg==");
                        String v2_1 = v4_1.preInvoke(10216, "android/net/NetworkInfo", "getType", v9, v10, "int", v11_1);
                        if (!v2_1.intercept) {
                            v1_2 = v9.getType();
                            v4_1.postInvoke(Integer.valueOf(v1_2), 10216, "android/net/NetworkInfo", "getType", v9, v10, v11_1, 1);
                            v0_4.L("active_network_info_type", v1_2);
                            X.4br.L("no_internet_connection_page_active_network_info", v0_4.L);
                        } else {
                            v4_1.postInvoke(0, 10216, "android/net/NetworkInfo", "getType", v9, v10, v11_1, 0);
                            v1_2 = ((Integer) v2_1.returnValue).intValue();
                        }
                    } else {
                        v1_2 = -1;
                    }
                }
                if (X.5uK.LB().L) {
                    if ((X.75K.L()) || (X.5uK.LB().LB)) {
                        if (X.5uV.L()) {
                            if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                                X.5uC.L = Y.ACallableS4S0200000_2.L$0(v3_3);
                                v9 = X.5uC.L;
                            } else {
                                if (X.5uO.L) {
                                    X.5uQ.L("cm_net_info", Y.ACallableS4S0200000_2.L$0(v3_3).toString(), X.5uC.L.toString());
                                }
                                v9 = X.5uC.L;
                            }
                        } else {
                            X.5uC.L = 0;
                            v9 = Y.ACallableS4S0200000_2.L$0(v3_3);
                        }
                    } else {
                        v9 = Y.ACallableS4S0200000_2.L$0(v3_3);
                    }
                } else {
                    v9 = Y.ACallableS4S0200000_2.L$0(v3_3);
                }
            }
        } else {
            v0_4 = new X.4DB();
            v1_2 = 1;
        }
        return kotlin.Unit.L;
    }

/**
Y.ACallableS4S0200000_2;call()Ljava/lang/Object;
*/

    public final synthetic Object call()
    {
        switch (this.$t) {
            case 0:
                return Y.ACallableS4S0200000_2.call$0(this);
            case 1:
                return Y.ACallableS4S0200000_2.call$1(this);
            case 2:
                return Y.ACallableS4S0200000_2.call$2(this);
            case 3:
                return Y.ACallableS4S0200000_2.call$3(this);
            case 4:
                return Y.ACallableS4S0200000_2.call$4(this);
            case 5:
                return Y.ACallableS4S0200000_2.call$5(this);
            case 6:
                return Y.ACallableS4S0200000_2.call$6(this);
            case 7:
                return Y.ACallableS4S0200000_2.call$7(this);
            case 8:
                return Y.ACallableS4S0200000_2.call$8(this);
            case 9:
                return Y.ACallableS4S0200000_2.call$9(this);
            case 10:
                return Y.ACallableS4S0200000_2.call$10(this);
            case 11:
                return Y.ACallableS4S0200000_2.call$11(this);
            case 12:
                return Y.ACallableS4S0200000_2.call$12(this);
            case 13:
                return Y.ACallableS4S0200000_2.call$13(this);
            case 14:
                return Y.ACallableS4S0200000_2.call$14(this);
            case 15:
                return Y.ACallableS4S0200000_2.call$15(this);
            case 16:
                return Y.ACallableS4S0200000_2.call$16(this);
            case 17:
                return Y.ACallableS4S0200000_2.call$17(this);
            case 18:
                return Y.ACallableS4S0200000_2.call$18(this);
            case 19:
                return Y.ACallableS4S0200000_2.call$19(this);
            case 20:
                return Y.ACallableS4S0200000_2.call$20(this);
            case 21:
                return Y.ACallableS4S0200000_2.call$21(this);
            case 22:
                return Y.ACallableS4S0200000_2.call$22(this);
            case 23:
                return Y.ACallableS4S0200000_2.call$23(this);
            case 24:
                return Y.ACallableS4S0200000_2.call$24(this);
            case 25:
                return Y.ACallableS4S0200000_2.call$25(this);
            case 26:
                return Y.ACallableS4S0200000_2.call$26(this);
            case 27:
                return Y.ACallableS4S0200000_2.call$27(this);
            case 28:
                return Y.ACallableS4S0200000_2.call$28(this);
            case 29:
                return Y.ACallableS4S0200000_2.call$29(this);
            case 30:
                return Y.ACallableS4S0200000_2.call$30(this);
            case 31:
                return Y.ACallableS4S0200000_2.call$31(this);
            case 32:
                return Y.ACallableS4S0200000_2.call$32(this);
            case 33:
                return Y.ACallableS4S0200000_2.call$33(this);
            case 34:
                return Y.ACallableS4S0200000_2.call$34(this);
            case 35:
                return Y.ACallableS4S0200000_2.call$35(this);
            case 36:
                return Y.ACallableS4S0200000_2.call$36(this);
            case 37:
                return Y.ACallableS4S0200000_2.call$37(this);
            case 38:
                return Y.ACallableS4S0200000_2.call$38(this);
            case 39:
                return Y.ACallableS4S0200000_2.call$39(this);
            case 40:
                return Y.ACallableS4S0200000_2.call$40(this);
            case 41:
                return Y.ACallableS4S0200000_2.call$41(this);
            case 42:
                return Y.ACallableS4S0200000_2.call$42(this);
            case 43:
                return Y.ACallableS4S0200000_2.call$43(this);
            case 44:
                return Y.ACallableS4S0200000_2.call$44(this);
            case 45:
                return Y.ACallableS4S0200000_2.call$45(this);
            case 46:
                return Y.ACallableS4S0200000_2.call$46(this);
            case 47:
                return Y.ACallableS4S0200000_2.call$47(this);
            case 48:
                return Y.ACallableS4S0200000_2.call$48(this);
            case 49:
                return Y.ACallableS4S0200000_2.call$49(this);
            case 50:
                return Y.ACallableS4S0200000_2.call$50(this);
            case 51:
                return Y.ACallableS4S0200000_2.call$51(this);
            case 52:
                return Y.ACallableS4S0200000_2.call$52(this);
            case 53:
                return Y.ACallableS4S0200000_2.call$53(this);
            case 54:
                return Y.ACallableS4S0200000_2.call$54(this);
            case 55:
                return Y.ACallableS4S0200000_2.call$55(this);
            case 56:
                return Y.ACallableS4S0200000_2.call$56(this);
            case 57:
                return Y.ACallableS4S0200000_2.call$57(this);
            case 58:
                return Y.ACallableS4S0200000_2.call$58(this);
            case 59:
                return Y.ACallableS4S0200000_2.call$59(this);
            case 60:
                return Y.ACallableS4S0200000_2.call$60(this);
            case 61:
                return Y.ACallableS4S0200000_2.call$61(this);
            case 62:
                return Y.ACallableS4S0200000_2.call$62(this);
            default:
                return 0;
        }
    }


}