/*Application Package Name: com.tiktok.lite.go
class PRCS_178 {
/**
X.3Oy;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28ad");
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
X.3Oy;LB()Z
*/

    public final boolean LB()
    {
        this.LFFLLL();
        android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) this.LIIII.L.getSystemService("connectivity"));
        android.net.NetworkInfo v4 = 0;
        if (v3_1 != null) {
            try {
                System.nanoTime();
            } catch (Exception) {
                if (v4 != null) {
                    if (v4.isConnected()) {
                        return 1;
                    }
                }
            }
            if (X.5uL.L()) {
                if ((X.75K.L()) || (X.5uK.LBL())) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.3Oy.L(v3_1);
                            v4 = X.5uC.L;
                        } else {
                            if (X.5uO.L) {
                                X.5uL.L("cm_net_info", X.3Oy.L(v3_1).toString(), X.5uC.L.toString());
                            }
                            v4 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v4 = X.3Oy.L(v3_1);
                    }
                } else {
                    v4 = X.3Oy.L(v3_1);
                }
            } else {
                v4 = X.3Oy.L(v3_1);
            }
        }
        return 0;
    }

/**
X.3P0;L(Landroid/content/Intent;)V
*/

    private void L(android.content.Intent p4)
    {
        this.L.LFFLLL();
        String v2 = p4.getAction();
        this.L.ag_().LFFFF.L("NetworkBroadcastReceiver received action", v2);
        if (!"android.net.conn.CONNECTIVITY_CHANGE".equals(v2)) {
            this.L.ag_().LCCII.L("NetworkBroadcastReceiver received unknown action", v2);
            return;
        } else {
            X.3Oz v0_7 = this.L.LFFFF;
            X.3RZ.L(v0_7);
            X.3PP v1_1 = v0_7.LB();
            if (this.LBL != v1_1) {
                this.LBL = v1_1;
                this.L.ah_().LB(new X.3Oz(this));
            }
            return;
        }
    }


}