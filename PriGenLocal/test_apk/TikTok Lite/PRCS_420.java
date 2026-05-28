/*Application Package Name: com.tiktok.lite.go
class PRCS_420 {
/**
X.7Qr;L(Landroid/content/Context; Landroid/content/Intent;)I
*/

    public final int L(android.content.Context p22, android.content.Intent p23)
    {
        int v4 = 10;
        if (p22 != null) {
            try {
                if (((android.net.ConnectivityManager) p22.getSystemService("connectivity")) != null) {
                    int v0_3 = -1;
                    if (p23 == null) {
                        if (!this.LCI) {
                            Integer v1_10;
                            android.net.wifi.WifiInfo v10 = X.1OF.L(((android.net.wifi.WifiManager) p22.getApplicationContext().getSystemService("wifi")), "dzBzEgAjS8/YVFkiQFyUaP/mqC5RLlqtbe3gIsdOVcSzDVFLDDbsyDm0XyAPCDatnQ==");
                            if (v10 != null) {
                                Integer v1_7;
                                com.bytedance.helios.statichook.api.HeliosApiHook v5_2 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                Object[] v11 = new Object[0];
                                com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgAjS8/YVFkiQFyUaP/mqC5RLlqtbe3gIsdOVcSzDVFLDDbsyDm0XyAPCDatnQ==");
                                com.bytedance.helios.statichook.api.Result v2_2 = v5_2.preInvoke(10228, "android/net/wifi/WifiInfo", "getRssi", v10, v11, "int", v12_1);
                                if (!v2_2.intercept) {
                                    v1_7 = v10.getRssi();
                                    v5_2.postInvoke(Integer.valueOf(v1_7), 10228, "android/net/wifi/WifiInfo", "getRssi", v10, v11, v12_1, 1);
                                } else {
                                    v5_2.postInvoke(0, 10228, "android/net/wifi/WifiInfo", "getRssi", v10, v11, v12_1, 0);
                                    v1_7 = ((Integer) v2_2.returnValue).intValue();
                                }
                                v1_10 = Integer.valueOf(v1_7);
                            } else {
                                v1_10 = 0;
                            }
                            v0_3 = v1_10.intValue();
                        }
                    } else {
                        v0_3 = p23.getIntExtra("newRssi", -70);
                    }
                    v4 = (android.net.wifi.WifiManager.calculateSignalLevel(v0_3, 4) + 1);
                    return v4;
                } else {
                    return 10;
                }
            } catch (int v0_6) {
                X.7U9.LC("TTNetWorkListener", v0_6.toString());
                return v4;
            }
        } else {
            return 10;
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

/**
X.7Qr;L(LX/7Qr; Landroid/content/Context; Landroid/content/Intent;)V
*/

    public static void L(X.7Qr p2, android.content.Context p3, android.content.Intent p4)
    {
        if ("android.net.conn.CONNECTIVITY_CHANGE".equals(p4.getAction())) {
            p2.LB(p3, p4);
            return;
        } else {
            p2.LB(p3, p4);
            return;
        }
    }


}