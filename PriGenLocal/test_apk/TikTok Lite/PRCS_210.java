/*Application Package Name: com.tiktok.lite.go
class PRCS_210 {
/**
com.google.android.gms.internal.gtm.be;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yz1cEJOnFpNPfG57TP3DlRLqg==");
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
com.google.android.gms.internal.gtm.be;LCC(Lcom/google/android/gms/internal/gtm/be;)Z
*/

    public static final boolean LCC(com.google.android.gms.internal.gtm.be p4)
    {
        android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) p4.LB.L.getSystemService("connectivity"));
        try {
            android.net.NetworkInfo v0_11;
            System.nanoTime();
        } catch (Exception) {
            return 0;
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = com.google.android.gms.internal.gtm.be.L(v3_1);
                        v0_11 = X.5uC.L;
                        if ((v0_11 == null) || (!v0_11.isConnected())) {
                            return 0;
                        } else {
                            return 1;
                        }
                    } else {
                        if (X.5uO.L) {
                            X.5uL.L("cm_net_info", com.google.android.gms.internal.gtm.be.L(v3_1).toString(), X.5uC.L.toString());
                        }
                        v0_11 = X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    v0_11 = com.google.android.gms.internal.gtm.be.L(v3_1);
                }
            } else {
                v0_11 = com.google.android.gms.internal.gtm.be.L(v3_1);
            }
        } else {
            v0_11 = com.google.android.gms.internal.gtm.be.L(v3_1);
        }
    }

/**
X.3Gk;LCC()V
*/

    public final void LCC()
    {
        X.37f.LB();
        this.LFI();
        if ((this.LFFL) || (this.LIIIII() <= 0)) {
            this.LCCII.LB();
            this.LIIII();
            return;
        } else {
            if (!this.LC.LCC()) {
                if (!((Boolean) X.3Fr.LIIILL.L).booleanValue()) {
                    long v3_1 = this.LCCII;
                    com.google.android.gms.internal.gtm.be.LC(v3_1);
                    if (!v3_1.LBL) {
                        X.3G2 v2_3 = v3_1.LB.L;
                        com.google.android.gms.internal.gtm.be.L(v2_3, v3_1, new android.content.IntentFilter("android.net.conn.CONNECTIVITY_CHANGE"));
                        Long v1_6 = new android.content.IntentFilter("com.google.analytics.RADIO_POWERED");
                        v1_6.addCategory(v2_3.getPackageName());
                        com.google.android.gms.internal.gtm.be.L(v2_3, v3_1, v1_6);
                        v3_1.LC = com.google.android.gms.internal.gtm.be.LCC(v3_1);
                        v3_1.LB.L().L("Registering connectivity change receiver. Network connected", Boolean.valueOf(v3_1.LC));
                        v3_1.LBL = 1;
                    }
                    X.3G2 v2_5 = this.LCCII;
                    if (!v2_5.LBL) {
                        v2_5.LB.L().LCC("Connectivity unknown. Receiver not registered");
                    }
                    if (!v2_5.LC) {
                        this.LIIII();
                        this.LIII();
                        return;
                    }
                }
                X.3G2 v2_7;
                this.LIII();
                long v4_1 = this.LIIIII();
                X.3G2 v2_6 = this.LFF().LC();
                if (v2_6 == 0) {
                    v2_7 = Math.min(X.3Fl.LC(), v4_1);
                } else {
                    v2_7 = (v4_1 - Math.abs((this.LB.LBL.L() - v2_6)));
                    if (v2_7 <= 0) {
                        v2_7 = Math.min(X.3Fl.LC(), v4_1);
                    }
                }
                this.L("Dispatch scheduled (ms)", Long.valueOf(v2_7));
                if (!this.LF.LBL()) {
                    this.LF.L(v2_7);
                    return;
                } else {
                    String v0_4;
                    Long v1_0 = this.LF;
                    if (v1_0.LB != 0) {
                        v0_4 = Math.abs((v1_0.L.LBL.L() - v1_0.LB));
                    } else {
                        v0_4 = 0;
                    }
                    long v7_0 = Math.max(1, (v2_7 + v0_4));
                    X.3G2 v2_1 = this.LF;
                    if (v2_1.LBL()) {
                        long v3_0 = 0;
                        if (v7_0 >= 0) {
                            long v7_1 = (v7_0 - Math.abs((v2_1.L.LBL.L() - v2_1.LB)));
                            if (v7_1 >= 0) {
                                v3_0 = v7_1;
                            }
                            X.3FW.LCC(v2_1).removeCallbacks(v2_1.LC);
                            if (!X.3FW.LCC(v2_1).postDelayed(v2_1.LC, v3_0)) {
                                v2_1.L.L().LCC("Failed to adjust delayed post. time", Long.valueOf(v3_0));
                                return;
                            }
                        } else {
                            v2_1.LC();
                        }
                    }
                    return;
                }
            } else {
                this.LCCII.LB();
                this.LIIII();
                return;
            }
        }
    }


}