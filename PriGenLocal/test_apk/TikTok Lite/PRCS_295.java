/*Application Package Name: com.tiktok.lite.go
class PRCS_295 {
/**
X.7Qr;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEd7IQ14lQB2BaMaCmTvFgfamkEiHWSoOWe4IxY190E4=");
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