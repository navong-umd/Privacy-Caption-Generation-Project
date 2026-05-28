/*Application Package Name: com.tiktok.lite.go
class PRCS_374 {
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

/**
com.ss.android.ugc.aweme.legoImpl.task.CommonParamsInitTask;LBL()Ljava/util/HashMap;
*/

    public static java.util.HashMap LBL()
    {
        java.util.HashMap v3_1 = new java.util.HashMap();
        v3_1.put("app_language", X.4Bg.L(X.4Bq.L()));
        v3_1.put("build_number", X.16B.LCCII.LB);
        v3_1.put("locale", X.4Bq.LB());
        v3_1.put("timezone_offset", String.valueOf((java.util.TimeZone.getDefault().getRawOffset() / 1000)));
        v3_1.put("carrier_region", X.5WL.LD());
        v3_1.put("region", X.4Bg.LC());
        v3_1.put("app_package", X.16B.LB.getPackageName());
        v3_1.put("op_region", X.5WL.L());
        String v2 = "unknown";
        try {
            String v1_6;
            if (android.os.Build.SUPPORTED_ABIS.length <= 0) {
                v1_6 = android.os.Build.CPU_ABI;
                if (!android.text.TextUtils.isEmpty(v1_6)) {
                    v2 = v1_6;
                }
            } else {
                v1_6 = android.os.Build.SUPPORTED_ABIS[0];
            }
        } catch (Exception) {
        }
        v3_1.put("host_abi", v2);
        v3_1.put("ts", String.valueOf(X.5WA.L()));
        v3_1.put("ac2", String.valueOf(X.0cD.LCCII(X.16B.LB)));
        return v3_1;
    }


}