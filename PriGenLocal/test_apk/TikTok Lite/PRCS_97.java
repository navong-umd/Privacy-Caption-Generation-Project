/*Application Package Name: com.tiktok.lite.go
class PRCS_97 {
/**
X.7So;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEd7IQ14lQB2BaMaCmTvFu8ec23K1Qg0RfOtc");
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
X.7So;L(Landroid/content/Context;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.content.Context p5)
    {
        if (p5 != null) {
            try {
                if (!X.7So.L) {
                    try {
                        if (!X.7So.L) {
                            X.7So.L = 1;
                            X.7So.L(p5.getApplicationContext(), X.7So.LB, new android.content.IntentFilter("android.net.conn.CONNECTIVITY_CHANGE"));
                        }
                    } catch (android.net.NetworkInfo v0_2) {
                        throw v0_2;
                    }
                }
            } catch (Exception) {
                return 0;
            }
            android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) p5.getSystemService("connectivity"));
            System.nanoTime();
            if (X.5uK.LB().L) {
                if ((X.75K.L()) || (X.5uK.LB().LB)) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.7So.L(v3_1);
                            return X.5uC.L;
                        } else {
                            if (X.5uO.L) {
                                X.5uQ.L("cm_net_info", X.7So.L(v3_1).toString(), X.5uC.L.toString());
                            }
                            return X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        return X.7So.L(v3_1);
                    }
                } else {
                    return X.7So.L(v3_1);
                }
            } else {
                return X.7So.L(v3_1);
            }
        } else {
            return 0;
        }
    }

/**
X.7So;LB(Landroid/content/Context;)Z
*/

    public static boolean LB(android.content.Context p0)
    {
        int v0_1 = X.7So.L(p0);
        if ((v0_1 == 0) || (!v0_1.isConnected())) {
            return 0;
        } else {
            return 1;
        }
    }


}