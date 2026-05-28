/*Application Package Name: com.tiktok.lite.go
class PRCS_200 {
/**
X.7Gk;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEcvSUUUuTBbKc9NnF3E3f2I9cuO+ZtHK3SZlA45xXxehMNG7TjUmcKElHsEi3zF+kRQ=");
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
X.7Gk;L(Landroid/content/Context;)Z
*/

    public static boolean L(android.content.Context p5)
    {
        try {
            android.net.ConnectivityManager v3_0 = p5.getSystemService("connectivity");
            java.util.Objects.requireNonNull(v3_0);
            android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) v3_0);
        } catch (Exception) {
            return 0;
        }
        android.net.NetworkInfo v0_11;
        System.nanoTime();
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.7Gk.L(v3_1);
                        v0_11 = X.5uC.L;
                        if ((v0_11 == null) || (!v0_11.isConnected())) {
                            return 0;
                        } else {
                            return 1;
                        }
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", X.7Gk.L(v3_1).toString(), X.5uC.L.toString());
                        }
                        v0_11 = X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    v0_11 = X.7Gk.L(v3_1);
                }
            } else {
                v0_11 = X.7Gk.L(v3_1);
            }
        } else {
            v0_11 = X.7Gk.L(v3_1);
        }
    }

/**
X.7Gj;onAvailable(Landroid/net/Network;)V
*/

    public final void onAvailable(android.net.Network p4)
    {
        super.onAvailable(p4);
        boolean v2 = X.7Gk.L(this.L);
        if (v2 != X.7Gk.L) {
            X.7Gg v1 = X.7Gf.L();
            if (!v1.LBL) {
                Integer v0_3 = ((X.7rA) X.7Fg.L(0));
                if ((v0_3 != null) && (v0_3.LC() != null)) {
                    v1.L(Integer.valueOf(5));
                }
            }
        }
        X.7Gk.L = v2;
        return;
    }


}