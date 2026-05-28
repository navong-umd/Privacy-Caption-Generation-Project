/*Application Package Name: com.tiktok.lite.go
class PRCS_117 {
/**
X.0cD;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgAjS8/YVFkiQFyHacu2SzYe/7zTjpfgl8thoe1CgUDWai5Rr1Y=");
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
X.0cD;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_20) {
            X.5If.L(v0_20);
            return X.0cD.L(p3);
        }
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.0cD.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", X.0cD.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.0cD.L(p3);
                }
            } else {
                return X.0cD.L(p3);
            }
        } else {
            return X.0cD.L(p3);
        }
    }

/**
X.0cD;LCCII(Landroid/content/Context;)Ljava/lang/String;
*/

    public static String LCCII(android.content.Context p21)
    {
        try {
            int v2_11 = X.0cD.LB(((android.net.ConnectivityManager) p21.getSystemService("connectivity")));
        } catch (Throwable) {
            return "unknown";
        }
        if ((v2_11 == 0) || (!v2_11.isAvailable())) {
            return "none";
        } else {
            int v2_6 = X.0cD.L(v2_11, "dzBzEgAjS8/YVFkiQFyHacu2SzYe/7zTjpfgl8thoe1CgUDWai5Rr1Y=");
            String v0_1 = 1;
            if (1 != v2_6) {
                if (v2_6 != 0) {
                    return "unknown";
                } else {
                    android.telephony.TelephonyManager v1_2 = ((android.telephony.TelephonyManager) p21.getSystemService("phone"));
                    switch (X.0cD.L(v1_2)) {
                        case 1:
                            return "gprs";
                        case 2:
                            return "edge";
                        case 3:
                            return "umts";
                        case 4:
                            return "cdma";
                        case 5:
                            return "evdo_0";
                        case 6:
                            return "evdo_a";
                        case 7:
                            return "1xrtt";
                        case 8:
                            return "hsdpa";
                        case 9:
                            return "hsupa";
                        case 10:
                            return "hspa";
                        case 11:
                            return "iden";
                        case 12:
                            return "evdo_b";
                        case 13:
                            return "lte";
                        case 14:
                            return "ehrpd";
                        case 15:
                            return "hspap";
                        case 16:
                            return "gsm";
                        case 17:
                            return "td_scdma";
                        case 18:
                        default:
                            return String.valueOf(X.0cD.L(v1_2));
                        case 19:
                            return "lte_ca";
                        case 20:
                            return "nr";
                    }
                }
            } else {
                int v2_3;
                android.net.wifi.WifiInfo v10_1 = X.1OF.L(((android.net.wifi.WifiManager) p21.getApplicationContext().getSystemService("wifi")), "dzBzEgAjS8/YVFkiQFyUaP/mqC5RLlqtbe3gIsdOVcSzDVFLDDbsyDm0XyAPCDatnQ==");
                if (v10_1 != null) {
                    int v2_0;
                    com.bytedance.helios.statichook.api.HeliosApiHook v5_3 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                    Object[] v11_1 = new Object[0];
                    com.bytedance.helios.statichook.api.ExtraInfo v12_2 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgAjS8/YVFkiQFyUaP/mqC5RLlqtbe3gIsdOVcSzDVFLDDbsyDm0XyAPCDatnQ==");
                    int v3_2 = v5_3.preInvoke(10229, "android/net/wifi/WifiInfo", "getFrequency", v10_1, v11_1, "int", v12_2);
                    if (!v3_2.intercept) {
                        v2_0 = v10_1.getFrequency();
                        v5_3.postInvoke(Integer.valueOf(v2_0), 10229, "android/net/wifi/WifiInfo", "getFrequency", v10_1, v11_1, v12_2, 1);
                    } else {
                        v5_3.postInvoke(0, 10229, "android/net/wifi/WifiInfo", "getFrequency", v10_1, v11_1, v12_2, 0);
                        v2_0 = ((Integer) v3_2.returnValue).intValue();
                    }
                    v2_3 = Integer.valueOf(v2_0);
                } else {
                    v2_3 = 0;
                }
                int v3_1;
                if (v2_3 == 0) {
                    v3_1 = -1;
                } else {
                    v3_1 = v2_3.intValue();
                }
                if ((v3_1 <= 4900) || (v3_1 >= 5900)) {
                    v0_1 = 0;
                }
                if (v0_1 == null) {
                    return "wifi";
                } else {
                    return "wifi5g";
                }
            }
        }
    }


}