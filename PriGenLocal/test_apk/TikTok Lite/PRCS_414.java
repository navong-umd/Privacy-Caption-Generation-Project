/*Application Package Name: com.tiktok.lite.go
class PRCS_414 {
/**
X.4Kc;LB()Z
*/

    public static boolean LB()
    {
        int v0_0 = X.4Kc.LBL();
        if (v0_0 == 0) {
            return 0;
        } else {
            int v1 = v0_0.getWifiState();
            if ((v1 == 2) || (v1 == 3)) {
                return 1;
            } else {
                return 0;
            }
        }
    }

/**
X.4Kc;L(Landroid/net/wifi/WifiManager; Landroid/app/Activity; Lkotlin/jvm/functions/Function1;)Z
*/

    public static boolean L(android.net.wifi.WifiManager p8, android.app.Activity p9, kotlin.jvm.functions.Function1 p10)
    {
        android.app.Application v5 = p9.getApplication();
        X.7Z7 v4_1 = new X.7Z7();
        v4_1.element = X.4Kc.LB;
        X.4Kb v6_1 = new X.4Kb(v4_1);
        v4_1.element = new Y.ARunnableS0S0400000_1(p10, v4_1, v5, v6_1, 2);
        X.4Kc.L(v5, v6_1, new android.content.IntentFilter("android.net.wifi.STATE_CHANGE"));
        X.4Kc.L.postDelayed(((Runnable) v4_1.element), 30000);
        try {
            if (p8.setWifiEnabled(1)) {
                if (X.4Kc.LB()) {
                    ((Runnable) v4_1.element).run();
                }
                return 1;
            } else {
                return 0;
            }
        } catch (Exception) {
            return 0;
        }
    }

/**
X.4Kc;L(Landroid/app/Activity; Lkotlin/jvm/functions/Function1;)V
*/

    public static void L(android.app.Activity p4, kotlin.jvm.functions.Function1 p5)
    {
        android.net.wifi.WifiManager v3 = X.4Kc.LBL();
        Boolean v2 = Boolean.valueOf(0);
        if (v3 != null) {
            if (!X.4Kc.L()) {
                if (android.os.Build$VERSION.SDK_INT >= 29) {
                    if (X.4Kc.LB(p4, p5)) {
                        return;
                    } else {
                        if (X.4Kc.L(v3, p4, p5)) {
                            return;
                        }
                    }
                } else {
                    if ((X.4Kc.L(v3, p4, p5)) || (X.4Kc.LB(p4, p5))) {
                        return;
                    }
                }
                android.content.Intent v1_1 = p4.getApplication();
                v1_1.registerActivityLifecycleCallbacks(new X.4Ka(v1_1, p5));
                try {
                    X.4Kc.L(p4, new android.content.Intent("android.settings.WIRELESS_SETTINGS"), "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPmtd4vH0jV92xn0HfnXdxaD5lZV");
                    return;
                } catch (Exception) {
                    p5.invoke(v2);
                    return;
                }
            } else {
                p5.invoke(Boolean.valueOf(1));
                return;
            }
        } else {
            p5.invoke(v2);
            return;
        }
    }


}