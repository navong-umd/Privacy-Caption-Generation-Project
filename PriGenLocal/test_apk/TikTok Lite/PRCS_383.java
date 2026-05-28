/*Application Package Name: com.tiktok.lite.go
class PRCS_383 {
/**
X.7Qr;L(Landroid/net/ConnectivityManager; I Ljava/lang/String;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p17, int p18, String p19)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v10 = new Object[1];
        v10[0] = Integer.valueOf(p18);
        com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/net/NetworkInfo;", p19);
        com.bytedance.helios.statichook.api.Result v1_0 = v4_1.preInvoke(195, "android/net/ConnectivityManager", "getNetworkInfo", p17, v10, "android.net.NetworkInfo", v11_1);
        if (!v1_0.intercept) {
            android.net.NetworkInfo v5_0 = p17.getNetworkInfo(p18);
            v4_1.postInvoke(v5_0, 195, "android/net/ConnectivityManager", "getNetworkInfo", p17, v10, v11_1, 1);
            return v5_0;
        } else {
            v4_1.postInvoke(0, 195, "android/net/ConnectivityManager", "getNetworkInfo", p17, v10, v11_1, 0);
            return ((android.net.NetworkInfo) v1_0.returnValue);
        }
    }

/**
X.7Qr;LB(Landroid/content/Context;)I
*/

    public static int LB(android.content.Context p8)
    {
        if (p8 != null) {
            android.net.ConnectivityManager v4_1 = ((android.net.ConnectivityManager) p8.getSystemService("connectivity"));
            if (v4_1 != null) {
                try {
                    android.net.NetworkInfo v5;
                    System.nanoTime();
                } catch (int v0_28) {
                    X.7U9.LC("TTNetWorkListener", v0_28.toString());
                    return 1000;
                }
                if (X.5uK.LB().L) {
                    if ((X.75K.L()) || (X.5uK.LB().LB)) {
                        if (X.5uV.L()) {
                            if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                                X.5uC.L = X.7Qr.L(v4_1);
                                v5 = X.5uC.L;
                                if ((v5 == null) || (!v5.isAvailable())) {
                                    return -1;
                                } else {
                                    int v0_21 = X.7Qr.L(v4_1, 1, "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4=");
                                    if (v0_21 != 0) {
                                        String v1_1 = v0_21.getState();
                                        if ((v1_1 != null) && ((v1_1 == android.net.NetworkInfo$State.CONNECTED) || (v1_1 == android.net.NetworkInfo$State.CONNECTING))) {
                                            return 0;
                                        }
                                    }
                                    int v0_24 = X.7Qr.L(v4_1, 0, "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4=");
                                    if (v0_24 != 0) {
                                        String v2_2 = v0_24.getState();
                                        String v1_2 = X.7Qr.L(v5, "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4=");
                                        if ((v2_2 != null) && ((v2_2 == android.net.NetworkInfo$State.CONNECTED) || (v2_2 == android.net.NetworkInfo$State.CONNECTING))) {
                                            return X.7Qr.LBL(v1_2);
                                        }
                                    }
                                    return 1000;
                                }
                            } else {
                                if (X.5uO.L) {
                                    X.5uQ.L("cm_net_info", X.7Qr.L(v4_1).toString(), X.5uC.L.toString());
                                }
                                v5 = X.5uC.L;
                            }
                        } else {
                            X.5uC.L = 0;
                            v5 = X.7Qr.L(v4_1);
                        }
                    } else {
                        v5 = X.7Qr.L(v4_1);
                    }
                } else {
                    v5 = X.7Qr.L(v4_1);
                }
            } else {
                return -1;
            }
        } else {
            return 1000;
        }
    }

/**
X.7Qr;LB(Landroid/content/Context; Landroid/content/Intent;)V
*/

    private void LB(android.content.Context p5, android.content.Intent p6)
    {
        if ((!this.isInitialStickyBroadcast()) && (p6 != null)) {
            if ((!"android.net.wifi.RSSI_CHANGED".equals(p6.getAction())) || (this.L != 0)) {
                if ("android.net.conn.CONNECTIVITY_CHANGE".equals(p6.getAction())) {
                    int v0_6 = X.7UB.L(X.7Sr.L.LF, 128);
                    this.LFF = v0_6;
                    if (v0_6 == 0) {
                        this.LB(X.7Qr.LB(p5));
                    } else {
                        int v0_12;
                        int v2_1 = p6.getIntExtra("networkType", -1);
                        android.net.NetworkInfo v1_3 = ((android.net.NetworkInfo) p6.getParcelableExtra("networkInfo"));
                        if ((v1_3 == null) || (v1_3.isConnected())) {
                            if (v2_1 != 0) {
                                if (v2_1 != 1) {
                                    v0_12 = 1000;
                                } else {
                                    v0_12 = 0;
                                }
                            } else {
                                if (v1_3 == null) {
                                    v0_12 = 1000;
                                } else {
                                    v0_12 = X.7Qr.LBL(X.7Qr.L(v1_3, "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4="));
                                }
                            }
                        } else {
                            v0_12 = -1;
                        }
                        this.LB(v0_12);
                        return;
                    }
                } else {
                    return;
                }
            } else {
                if (!X.7UB.L(X.7Sr.L.LF, 32)) {
                    this.L(this.L(p5, p6));
                }
                return;
            }
        }
        return;
    }


}