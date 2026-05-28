/*Application Package Name: com.tiktok.lite.go
class PRCS_243 {
/**
X.3YD;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBknTACBZOH3RnJ+RNEWrFftiFMy+rZGaM2SwFQJFRlGzc0=");
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
X.3YD;L()Z
*/

    public final declared_synchronized boolean L()
    {
        try {
            android.net.NetworkInfo v0_18;
            android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) this.LB.getSystemService("connectivity"));
        } catch (android.net.NetworkInfo v0_19) {
            throw v0_19;
        }
        if (v3_1 == null) {
            v0_18 = 0;
        } else {
            android.net.NetworkInfo v0_11;
            System.nanoTime();
            if (X.5uK.LB().L) {
                if ((X.75K.L()) || (X.5uK.LB().LB)) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.3YD.L(v3_1);
                            v0_11 = X.5uC.L;
                            if (v0_11 == null) {
                            } else {
                                v0_18 = v0_11.isConnected();
                            }
                        } else {
                            if (X.5uO.L) {
                                X.5uQ.L("cm_net_info", X.3YD.L(v3_1).toString(), X.5uC.L.toString());
                            }
                            v0_11 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v0_11 = X.3YD.L(v3_1);
                    }
                } else {
                    v0_11 = X.3YD.L(v3_1);
                }
            } else {
                v0_11 = X.3YD.L(v3_1);
            }
        }
        return v0_18;
    }

/**
X.3YC;L(Landroid/content/Context;)V
*/

    private declared_synchronized void L(android.content.Context p5)
    {
        try {
            int v0_0 = this.LB;
        } catch (int v0_2) {
            throw v0_2;
        }
        if (v0_0 != 0) {
            if (v0_0.L()) {
                this.LB.L.L(this.LB, 0);
                p5.unregisterReceiver(this);
                this.LB = 0;
                return;
            } else {
                return;
            }
        } else {
            return;
        }
    }


}