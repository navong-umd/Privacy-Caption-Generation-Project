/*Application Package Name: com.tiktok.lite.go
class PRCS_375 {
/**
X.1OF;L(Landroid/net/wifi/WifiManager; Ljava/lang/String;)Landroid/net/wifi/WifiInfo;
*/

    public static android.net.wifi.WifiInfo L(android.net.wifi.WifiManager p18, String p19)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v9 = new Object[0];
        com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/wifi/WifiInfo;", p19);
        com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(102301, "android/net/wifi/WifiManager", "getConnectionInfo", p18, v9, "android.net.wifi.WifiInfo", v10_1);
        if (!v1_0.intercept) {
            android.net.wifi.WifiInfo v4_0 = p18.getConnectionInfo();
            v3_1.postInvoke(v4_0, 102301, "android/net/wifi/WifiManager", "getConnectionInfo", p18, v9, v10_1, 1);
            return v4_0;
        } else {
            v3_1.postInvoke(0, 102301, "android/net/wifi/WifiManager", "getConnectionInfo", p18, v9, v10_1, 0);
            return ((android.net.wifi.WifiInfo) v1_0.returnValue);
        }
    }

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
X.7uv;run()V
*/

    public final void run()
    {
        try {
            if (android.os.Looper.myLooper() == null) {
                android.os.Looper.prepare();
            }
        } catch (String v0_27) {
            throw v0_27;
        }
        X.7Qq v2_3 = X.7UB.L();
        if ((v2_3 == 1) || ((v2_3 == 2) || (v2_3 == 3))) {
            X.7Qr.L().LCI = 1;
            X.7U9.L("TTNetWorkListener", "is wifi sensitive mode:".concat(String.valueOf(v2_3)));
        }
        X.7Qr v5 = X.7Qr.L();
        X.7Qq v2_1 = ((android.content.Context) this.L.get());
        android.telephony.TelephonyManager v1_2 = new android.content.IntentFilter();
        v1_2.addAction("android.net.conn.CONNECTIVITY_CHANGE");
        v1_2.addAction("android.net.wifi.RSSI_CHANGED");
        X.7Qr.L(v2_1, v5, v1_2);
        v5.LB(X.7Qr.LB(v2_1));
        if (v5.L == 0) {
            v5.LB = v5.L(v2_1, 0);
        }
        v5.LCCII = new X.7Qq(v2_1, v5);
        if (!v5.LCI) {
            X.7Qq v2_2 = v5.LCCII;
            if (v2_2.L != null) {
                if (android.os.Build$VERSION.SDK_INT >= 23) {
                    X.7Qq.L(v2_2.L, v2_2, 256, "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4=");
                }
                X.7Qq.L(v2_2.L, v2_2, 64, "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4=");
            }
        }
        v5.LCC = 1;
        android.os.Looper.loop();
        X.7Qq v2_5 = ((X.7Qr) this.LB.get());
        if (v2_5 != null) {
            android.telephony.TelephonyManager v1_7 = ((android.content.Context) this.L.get());
            if (v1_7 != null) {
                if (v2_5.LCCII != null) {
                    v1_7.unregisterReceiver(v2_5);
                    X.7Qq v2_6 = v2_5.LCCII;
                    if (v2_6.L != null) {
                        X.7Qq.L(v2_6.L, v2_6, 0, "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4=");
                    }
                    return;
                }
            }
        }
        return;
    }


}