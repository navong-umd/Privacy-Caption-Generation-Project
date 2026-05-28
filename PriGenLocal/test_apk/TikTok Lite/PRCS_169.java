/*Application Package Name: com.tiktok.lite.go
class PRCS_169 {
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
X.3RZ;LFI()V
*/

    public final void LFI()
    {
        this.ah_().ac_();
        this.LFFLLL();
        if (this.LIII > 0) {
            X.3Oo v4_2 = (3600000 - Math.abs((this.ae_().LB() - this.LIII)));
            if (v4_2 <= 0) {
                this.LIII = 0;
            } else {
                this.ag_().LFFFF.L("Upload has been suspended. Will update scheduling later in approximately ms", Long.valueOf(v4_2));
                this.LICI().LB();
                long v0_44 = this.LFFLLL;
                X.3RZ.L(v0_44);
                v0_44.LCC();
                return;
            }
        }
        if ((!this.LCC.LIIIIZ()) || (!this.LIII())) {
            this.ag_().LFFFF.L("Nothing to upload or uploading impossible");
            this.LICI().LB();
            long v0_46 = this.LFFLLL;
            X.3RZ.L(v0_46);
            v0_46.LCC();
            return;
        } else {
            X.3RN v2_62;
            long v0_48 = this.ae_().L();
            this.L();
            long v18 = Math.max(0, ((Long) X.3Oc.LIIJILLL.L(0)).longValue());
            Long v3_8 = this.L;
            X.3RZ.L(v3_8);
            if (X.3Rs.LB(v3_8, "select count(1) > 0 from raw_events where realtime = 1", 0) == 0) {
                v2_62 = 0;
            } else {
                v2_62 = 1;
            }
            long v6_0;
            int v17 = 1;
            if (v2_62 != null) {
                Long v3_13 = this.L().LC("debug.firebase.analytics.app");
                if ((android.text.TextUtils.isEmpty(v3_13)) || (".none.".equals(v3_13))) {
                    this.L();
                    v6_0 = Math.max(0, ((Long) X.3Oc.LIIIII.L(0)).longValue());
                } else {
                    this.L();
                    v6_0 = Math.max(0, ((Long) X.3Oc.LIIIIZ.L(0)).longValue());
                }
            } else {
                Long v3_10 = this.L;
                X.3RZ.L(v3_10);
                if (X.3Rs.LB(v3_10, "select count(1) > 0 from queue where has_realtime = 1", 0) != 0) {
                } else {
                    v17 = 0;
                    this.L();
                    v6_0 = Math.max(0, ((Long) X.3Oc.LIIII.L(0)).longValue());
                }
            }
            boolean v13_0 = this.LC.LBL.L();
            long v15_0 = this.LC.LC.L();
            Long v3_0 = this.L;
            X.3RZ.L(v3_0);
            X.3Oo v4_0 = X.3Rs.L(v3_0, "select max(bundle_end_timestamp) from queue", 0, 0);
            Long v3_1 = this.L;
            X.3RZ.L(v3_1);
            Long v3_2 = Math.max(v4_0, X.3Rs.L(v3_1, "select max(timestamp) from raw_events", 0, 0));
            if (v3_2 != 0) {
                int v10_0 = (v0_48 - Math.abs((v3_2 - v0_48)));
                boolean v13_2 = Math.abs((v13_0 - v0_48));
                X.3Oo v4_1 = (v0_48 - Math.abs((v15_0 - v0_48)));
                X.3RN v2_16 = Math.max((v0_48 - v13_2), v4_1);
                long v0_3 = (v10_0 + v18);
                if ((v17 != 0) && (v2_16 > 0)) {
                    v0_3 = (Math.min(v10_0, v2_16) + v6_0);
                }
                boolean v13_4 = this.LFI;
                X.3RZ.L(v13_4);
                if (!v13_4.L(v2_16, v6_0)) {
                    v0_3 = (v2_16 + v6_0);
                }
                if ((v4_1 != 0) && (v4_1 >= v10_0)) {
                    int v10_1 = 0;
                    while(true) {
                        this.L();
                        if (v10_1 >= Math.min(20, Math.max(0, ((Integer) X.3Oc.LIIL.L(0)).intValue()))) {
                            this.ag_().LFFFF.L("Next upload time is 0");
                            this.LICI().LB();
                            long v0_11 = this.LFFLLL;
                            X.3RZ.L(v0_11);
                            v0_11.LCC();
                            return;
                        } else {
                            this.L();
                            v0_3 += (Math.max(0, ((Long) X.3Oc.LIIJJILLDILLLLLILLLLLLLLLLLLLLL.L(0)).longValue()) * (1 << v10_1));
                            if (v0_3 > v4_1) {
                                break;
                            }
                            v10_1++;
                        }
                    }
                }
                if (v0_3 != 0) {
                    X.3RN v2_34 = this.LFFFF;
                    X.3RZ.L(v2_34);
                    if (!v2_34.LB()) {
                        this.ag_().LFFFF.L("No network");
                        Long v3_5 = this.LICI();
                        v3_5.L.LFFLLL();
                        v3_5.L.ah_().ac_();
                        if (!v3_5.LB) {
                            X.3P0.L(v3_5.L.LCC.L, v3_5, new android.content.IntentFilter("android.net.conn.CONNECTIVITY_CHANGE"));
                            long v0_24 = v3_5.L.LFFFF;
                            X.3RZ.L(v0_24);
                            v3_5.LBL = v0_24.LB();
                            v3_5.L.ag_().LFFFF.L("Registering connectivity change receiver. Network connected", Boolean.valueOf(v3_5.LBL));
                            v3_5.LB = 1;
                        }
                        long v0_32 = this.LFFLLL;
                        X.3RZ.L(v0_32);
                        v0_32.LCC();
                        return;
                    } else {
                        X.3Oo v4_3 = this.LC.LB.L();
                        this.L();
                        X.3RN v2_44 = Math.max(0, ((Long) X.3Oc.LII.L(0)).longValue());
                        long v6_4 = this.LFI;
                        X.3RZ.L(v6_4);
                        if (!v6_4.L(v4_3, v2_44)) {
                            v0_3 = Math.max(v0_3, (v4_3 + v2_44));
                        }
                        this.LICI().LB();
                        long v0_34 = (v0_3 - this.ae_().L());
                        if (v0_34 <= 0) {
                            this.L();
                            v0_34 = Math.max(0, ((Long) X.3Oc.LIIIIZZ.L(0)).longValue());
                            this.LC.LBL.L(this.ae_().L());
                        }
                        this.ag_().LFFFF.L("Upload scheduled in approximately ms", Long.valueOf(v0_34));
                        X.3RN v2_54 = this.LFFLLL;
                        X.3RZ.L(v2_54);
                        v2_54.L(v0_34);
                        return;
                    }
                }
            }
            this.ag_().LFFFF.L("Next upload time is 0");
            this.LICI().LB();
            v0_11 = this.LFFLLL;
            X.3RZ.L(v0_11);
            v0_11.LCC();
            return;
        }
    }


}