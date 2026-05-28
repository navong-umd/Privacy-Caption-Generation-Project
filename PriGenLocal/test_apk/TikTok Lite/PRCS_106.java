/*Application Package Name: com.tiktok.lite.go
class PRCS_106 {
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
X.7vG;LB()V
*/

    public final void LB()
    {
        int v0_0 = this;
        if (!this.LB) {
            if (this.LCCII < this.LFFL) {
                X.7Sj.L();
                if ((this.LD) || (!this.LF)) {
                    this.LCCII();
                    return;
                } else {
                    X.7Sk v6_2;
                    org.json.JSONObject v1_11;
                    android.net.NetworkInfo v10 = X.7So.L(this.LFI);
                    if ((v10 == null) || (!v10.isAvailable())) {
                        v6_2 = 0;
                        v1_11 = -1;
                    } else {
                        com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v11_0 = new Object[0];
                        com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEhEpEd7IQ14lQB2BaMaCmTvFu8ec23ieZQgEZ/S1BQ==");
                        org.json.JSONObject v4_2 = v5_1.preInvoke(10216, "android/net/NetworkInfo", "getType", v10, v11_0, "int", v12_1);
                        if (!v4_2.intercept) {
                            v1_11 = v10.getType();
                            v5_1.postInvoke(Integer.valueOf(v1_11), 10216, "android/net/NetworkInfo", "getType", v10, v11_0, v12_1, 1);
                        } else {
                            v5_1.postInvoke(0, 10216, "android/net/NetworkInfo", "getType", v10, v11_0, v12_1, 0);
                            v1_11 = ((Integer) v4_2.returnValue).intValue();
                        }
                        com.bytedance.helios.statichook.api.HeliosApiHook v5_3 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v11_1 = new Object[0];
                        com.bytedance.helios.statichook.api.ExtraInfo v12_3 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Ljava/lang/String;", "dzBzEhEpEd7IQ14lQB2BaMaCmTvFu8ec23ieZQgEZ/S1BQ==");
                        org.json.JSONObject v4_4 = v5_3.preInvoke(10218, "android/net/NetworkInfo", "getExtraInfo", v10, v11_1, "java.lang.String", v12_3);
                        if (!v4_4.intercept) {
                            v6_2 = v10.getExtraInfo();
                            v5_3.postInvoke(v6_2, 10218, "android/net/NetworkInfo", "getExtraInfo", v10, v11_1, v12_3, 1);
                        } else {
                            v5_3.postInvoke(0, 10218, "android/net/NetworkInfo", "getExtraInfo", v10, v11_1, v12_3, 0);
                            v6_2 = ((String) v4_4.returnValue);
                        }
                    }
                    if (v1_11 != -1) {
                        if (v1_11 == X.7Sl.L) {
                            X.7Si v2_0 = X.7Sl.LB;
                            if ((v6_2 == null) || ((v2_0 != null) && (v6_2.equals(v2_0)))) {
                                if (this.LF) {
                                    org.json.JSONObject v3_0 = this.LI;
                                    if ((v3_0 != null) && (v3_0.LBL != null)) {
                                        X.7Sk v6_1 = ((X.7Sk) v3_0.LBL.get(this.LBL));
                                        if (v6_1 != null) {
                                            if (android.os.SystemClock.elapsedRealtime() >= v6_1.LB) {
                                                this.LFLL = 1;
                                                v0_0 = this.LCCII();
                                            }
                                            v0_0.LFFFF = 1;
                                            try {
                                                v6_1.L.put("time", System.currentTimeMillis());
                                                v6_1.L.put("dns_type", "localDNS");
                                            } catch (Exception) {
                                            }
                                            if (v0_0.LC != null) {
                                                v0_0.LC.L(v6_1.L, 0);
                                            }
                                            return;
                                        }
                                    }
                                }
                                this.LCCII();
                                return;
                            } else {
                                System.currentTimeMillis();
                            }
                        } else {
                            System.currentTimeMillis();
                        }
                        org.json.JSONObject v3_3 = this.LI;
                        if (v3_3.LBL != null) {
                            v3_3.LBL.clear();
                        }
                        X.7Sl.LB = v6_2;
                        X.7Sl.L = v1_11;
                        this.LCCII();
                        return;
                    }
                }
            } else {
                return;
            }
        } else {
            return;
        }
    }


}