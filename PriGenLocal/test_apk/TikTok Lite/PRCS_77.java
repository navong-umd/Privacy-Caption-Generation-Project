/*Application Package Name: com.tiktok.lite.go
class PRCS_77 {
/**
X.1Z8;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgAjS8/YVFkiQFyXYrVAyWIUdI6xHaretw+PPS5ahKhGRAoZFw==");
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
X.1Z8;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_19) {
            X.5If.L(v0_19);
            return X.1Z8.L(p3);
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uL.LB()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.1Z8.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uL.LBL()) {
                            X.5uL.L("cm_net_info", X.1Z8.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.1Z8.L(p3);
                }
            } else {
                return X.1Z8.L(p3);
            }
        } else {
            return X.1Z8.L(p3);
        }
    }

/**
X.1Z8;L(Landroid/content/Context;)Z
*/

    public static boolean L(android.content.Context p2)
    {
        try {
            int v0_5 = X.1Z8.LB(((android.net.ConnectivityManager) p2.getSystemService("connectivity")));
        } catch (int v0_2) {
            v0_2.printStackTrace();
            return 0;
        }
        if ((v0_5 == 0) || (!v0_5.isAvailable())) {
            return 0;
        } else {
            return 1;
        }
    }


}