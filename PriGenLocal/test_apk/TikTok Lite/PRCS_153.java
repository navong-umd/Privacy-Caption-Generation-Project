/*Application Package Name: com.tiktok.lite.go
class PRCS_153 {
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
X.3RZ;L(Ljava/lang/String; I Ljava/lang/Throwable; [B Ljava/util/Map;)V
*/

    public final void L(String p10, int p11, Throwable p12, byte[] p13, java.util.Map p14)
    {
        this.ah_().ac_();
        this.LFFLLL();
        X.3D5.L(p10);
        try {
            if (p13 == null) {
                p13 = new byte[0];
            }
        } catch (boolean v0_31) {
            this.LIIII = 0;
            this.LII();
            throw v0_31;
        }
        X.3Oo v1_0 = this.ag_().LFFFF;
        Integer v5 = Integer.valueOf(p13.length);
        v1_0.L("onConfigFetched. Response size", v5);
        boolean v0_26 = this.L;
        X.3RZ.L(v0_26);
        v0_26.LCCII();
        boolean v0_35;
        boolean v0_32 = this.L;
        X.3RZ.L(v0_32);
        X.3Oo v3_5 = v0_32.LC(p10);
        if ((p11 == 200) || (p11 == 204)) {
            if (p12 != null) {
                v0_35 = 0;
            } else {
                v0_35 = 1;
            }
        } else {
            if (p11 != 304) {
            } else {
                p11 = 304;
            }
        }
        boolean v0_9;
        if (v3_5 != null) {
            if ((v0_35) || (p11 == 404)) {
                String v7_0;
                if (p14 == null) {
                    v7_0 = 0;
                } else {
                    X.3Oo v1_7 = ((java.util.List) p14.get("Last-Modified"));
                    if ((v1_7 == null) || (v1_7.isEmpty())) {
                    } else {
                        v7_0 = ((String) v1_7.get(0));
                    }
                }
                X.3Oo v1_11;
                X.3MK.LBL();
                if ((!this.L().LC(0, X.3Oc.LIZZ)) || (p14 == null)) {
                    v1_11 = 0;
                } else {
                    X.3Oo v1_10 = ((java.util.List) p14.get("ETag"));
                    if ((v1_10 == null) || (v1_10.isEmpty())) {
                    } else {
                        v1_11 = ((String) v1_10.get(0));
                    }
                }
                if ((p11 == 404) || (p11 == 304)) {
                    boolean v0_42 = this.LFF;
                    X.3RZ.L(v0_42);
                    if (v0_42.L(p10) == null) {
                        boolean v0_44 = this.LFF;
                        X.3RZ.L(v0_44);
                        if (!v0_44.L(p10, 0, 0, 0)) {
                            v0_9 = this.L;
                            X.3RZ.L(v0_9);
                            v0_9.LCI();
                            this.LIIII = 0;
                            this.LII();
                            return;
                        }
                    }
                } else {
                    boolean v0_46 = this.LFF;
                    X.3RZ.L(v0_46);
                    if (!v0_46.L(p10, p13, v7_0, v1_11)) {
                        v0_9 = this.L;
                        X.3RZ.L(v0_9);
                        v0_9.LCI();
                        this.LIIII = 0;
                        this.LII();
                        return;
                    }
                }
                v3_5.LB(this.ae_().L());
                boolean v0_51 = this.L;
                X.3RZ.L(v0_51);
                v0_51.L(v3_5);
                if (p11 != 404) {
                    this.ag_().LFFFF.L("Successfully fetched config. Got network response. code, size", Integer.valueOf(p11), v5);
                } else {
                    this.ag_().LD.L("Config not found. Using empty config. appId", p10);
                }
                boolean v0_6 = this.LFFFF;
                X.3RZ.L(v0_6);
                if ((!v0_6.LB()) || (!this.LIII())) {
                    this.LFI();
                    boolean v0_29 = this.L;
                    X.3RZ.L(v0_29);
                    v0_29.LF();
                    v0_9 = this.L;
                    X.3RZ.L(v0_9);
                } else {
                    this.LFLL();
                }
            } else {
                v3_5.LCC(this.ae_().L());
                boolean v0_12 = this.L;
                X.3RZ.L(v0_12);
                v0_12.L(v3_5);
                this.ag_().LFFFF.L("Fetching config failed. code, error", Integer.valueOf(p11), p12);
                boolean v0_15 = this.LFF;
                X.3RZ.L(v0_15);
                v0_15.ac_();
                v0_15.LCC.put(p10, 0);
                this.LC.LC.L(this.ae_().L());
                if ((p11 == 503) || (p11 == 429)) {
                    this.LC.LB.L(this.ae_().L());
                }
                this.LFI();
            }
        } else {
            this.ag_().LCCII.L("App does not exist in onConfigFetched. appId", X.3Or.L(p10));
        }
        v0_9.LCI();
        this.LIIII = 0;
        this.LII();
        return;
    }


}