/*Application Package Name: com.tiktok.lite.go
class PRCS_6 {
/**
X.3Ym;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBknTACBZOH3RnJ+RNEWrFftiFMy/aC0ruscZ7c=");
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
X.3Ym;L()Z
*/

    public final boolean L()
    {
        android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) this.L.LB.getSystemService("connectivity"));
        if (v3_1 != null) {
            try {
                android.net.NetworkInfo v0_13;
                System.nanoTime();
            } catch (android.net.NetworkInfo v0_19) {
                X.5If.L(v0_19);
                v0_13 = X.3Ym.L(v3_1);
            }
            if (X.5uK.LB().L) {
                if ((X.75K.L()) || (X.5uK.LB().LB)) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.3Ym.L(v3_1);
                            v0_13 = X.5uC.L;
                            if ((v0_13 != null) && (v0_13.isConnected())) {
                                return 1;
                            }
                        } else {
                            if (X.5uO.L) {
                                X.5uQ.L("cm_net_info", X.3Ym.L(v3_1).toString(), X.5uC.L.toString());
                            }
                            v0_13 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v0_13 = X.3Ym.L(v3_1);
                    }
                } else {
                    v0_13 = X.3Ym.L(v3_1);
                }
            } else {
                v0_13 = X.3Ym.L(v3_1);
            }
        }
        return 0;
    }

/**
X.3Yl;L()V
*/

    private void L()
    {
        int v0_0 = this.L;
        if (v0_0 != 0) {
            if (v0_0.L()) {
                com.google.firebase.messaging.FirebaseMessaging.L(this.L, 0);
                this.L.L.LB.unregisterReceiver(this);
                this.L = 0;
                return;
            } else {
                return;
            }
        } else {
            return;
        }
    }


}