/*Application Package Name: com.tiktok.lite.go
class PRCS_9 {
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
X.3Ym;run()V
*/

    public final void run()
    {
        if (X.3Yh.L().L(this.L.LB)) {
            this.LBL.acquire();
        }
        try {
            int v4 = 1;
            this.L.L(1);
        } catch (com.google.firebase.messaging.FirebaseMessaging v2_2) {
            if (X.3Yh.L().L(this.L.LB)) {
                this.LBL.release();
            }
            throw v2_2;
        }
        if (this.L.LBL.L()) {
            com.google.firebase.messaging.FirebaseMessaging v2_0 = X.3Yh.L();
            if (v2_0.LB == null) {
                if (this.L.LB.checkCallingOrSelfPermission("android.permission.ACCESS_NETWORK_STATE") != 0) {
                    v4 = 0;
                }
                v2_0.LB = Boolean.valueOf(v4);
            }
            if ((!v2_0.LB.booleanValue()) || (this.L())) {
                if (!this.LBL()) {
                    this.L.L(this.LB);
                } else {
                    this.L.L(0);
                }
                if (!X.3Yh.L().L(this.L.LB)) {
                    return;
                } else {
                    this.LBL.release();
                    return;
                }
            } else {
                com.google.firebase.messaging.FirebaseMessaging v2_4 = new X.3Yl(this);
                X.3Yl.L(v2_4.L.L.LB, v2_4, new android.content.IntentFilter("android.net.conn.CONNECTIVITY_CHANGE"));
                if (X.3Yh.L().L(this.L.LB)) {
                    this.LBL.release();
                }
                return;
            }
        } else {
            this.L.L(0);
            if (X.3Yh.L().L(this.L.LB)) {
                this.LBL.release();
            }
            return;
        }
    }


}