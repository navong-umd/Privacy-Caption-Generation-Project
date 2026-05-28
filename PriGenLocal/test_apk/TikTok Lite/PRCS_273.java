/*Application Package Name: com.tiktok.lite.go
class PRCS_273 {
/**
X.3vZ;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEcvSUUUuTBbKco0nino4eVEjSCTRZngWb97dUSY=");
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
X.3vZ;L()Z
*/

    public static boolean L()
    {
        if (X.3vZ.LB() != null) {
            try {
                android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) X.3vZ.LB().getSystemService("connectivity"));
            } catch (Exception) {
                return 0;
            }
            android.net.NetworkInfo v0_11;
            System.nanoTime();
            if (X.5uL.L()) {
                if ((X.75K.L()) || (X.5uK.LBL())) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.3vZ.L(v3_1);
                            v0_11 = X.5uC.L;
                            if ((v0_11 == null) || (!v0_11.isConnected())) {
                                return 0;
                            } else {
                                return 1;
                            }
                        } else {
                            if (X.5uO.L) {
                                X.5uL.L("cm_net_info", X.3vZ.L(v3_1).toString(), X.5uC.L.toString());
                            }
                            v0_11 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v0_11 = X.3vZ.L(v3_1);
                    }
                } else {
                    v0_11 = X.3vZ.L(v3_1);
                }
            } else {
                v0_11 = X.3vZ.L(v3_1);
            }
        } else {
            return 0;
        }
    }

/**
X.3ve;L(Z)V
*/

    private void L(boolean p9)
    {
        if (X.3ve.LFF) {
            if (this.LFI) {
                if (!this.LB) {
                    this.LB = 1;
                    this.LIII = 1;
                    if (X.3vZ.L()) {
                        if (X.3vZ.LBL()) {
                            java.util.HashMap v2_0;
                            this.LICI = 0;
                            X.3vU v0_4 = this.LCC.L;
                            int v1_1 = new StringBuilder();
                            v1_1.append(v0_4);
                            v1_1.append("/passport/token/beat/v2/");
                            String v3_2 = new X.1Z9(v1_1.toString());
                            if (!p9) {
                                v2_0 = "polling";
                            } else {
                                v2_0 = "boot";
                            }
                            if (!android.text.TextUtils.isEmpty(0)) {
                                v2_0 = 0;
                            }
                            int v1_3;
                            v3_2.L("scene", v2_0);
                            if (!this.LF) {
                                v1_3 = "false";
                            } else {
                                v1_3 = "true";
                            }
                            v3_2.L("first_beat", v1_3);
                            String v3_3 = v3_2.toString();
                            if (!android.text.TextUtils.isEmpty(v3_3)) {
                                this.LII = new X.3vc(this, v3_3);
                                X.3vZ.L(v3_3, new java.util.HashMap(), 0, 1, this.LII);
                            }
                        } else {
                            this.LCCII.sendEmptyMessageDelayed(1000, this.LCC.LC);
                            this.LB = 0;
                            return;
                        }
                    } else {
                        this.LICI = (this.LICI + 1);
                        this.LCCII.sendEmptyMessageDelayed(1000, Math.min((((long) this.LICI) * 10000), this.LCC.LC));
                        this.LB = 0;
                        return;
                    }
                }
                return;
            } else {
                return;
            }
        } else {
            return;
        }
    }


}