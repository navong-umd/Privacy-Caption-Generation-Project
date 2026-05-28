/*Application Package Name: com.tiktok.lite.go
class PRCS_263 {
/**
X.3vZ;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEcvSUUUuTBbKco0nino4eVEjSCTRZngWb97dUSY=");
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
X.3vZ;L()Z
*/

    public static boolean L()
    {
        if (X.3vZ.LB() != null) {
            try {
                android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) X.3vZ.LB().getSystemService("connectivity"));
            } catch (Exception) {
                return 0;
            }
            android.net.NetworkInfo v0_11;
            System.nanoTime();
            if (X.5uL.L()) {
                if ((X.75K.L()) || (X.5uK.LBL())) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.3vZ.L(v3_1);
                            v0_11 = X.5uC.L;
                            if ((v0_11 == null) || (!v0_11.isConnected())) {
                                return 0;
                            } else {
                                return 1;
                            }
                        } else {
                            if (X.5uO.L) {
                                X.5uL.L("cm_net_info", X.3vZ.L(v3_1).toString(), X.5uC.L.toString());
                            }
                            v0_11 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v0_11 = X.3vZ.L(v3_1);
                    }
                } else {
                    v0_11 = X.3vZ.L(v3_1);
                }
            } else {
                v0_11 = X.3vZ.L(v3_1);
            }
        } else {
            return 0;
        }
    }

/**
X.3va;L(Ljava/lang/String; Ljava/lang/String; Lorg/json/JSONObject;)V
*/

    public static void L(String p1, String p2, org.json.JSONObject p3)
    {
        try {
            if (p3 == null) {
                p3 = new org.json.JSONObject();
            }
        } catch (String v0_2) {
            v0_2.printStackTrace();
            return;
        }
        p3.put("error_name", p1);
        p3.put("error_message", p2);
        int v2_1 = 1;
        p3.put("network_available", X.3vZ.L());
        if (X.1Z5.L <= 0) {
            v2_1 = 0;
        }
        p3.put("app_in_foreground", v2_1);
        X.3va.L("token_config_err_v2", p3);
        return;
    }


}