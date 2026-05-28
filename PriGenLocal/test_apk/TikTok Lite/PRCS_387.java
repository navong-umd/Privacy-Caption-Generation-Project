/*Application Package Name: com.tiktok.lite.go
class PRCS_387 {
/**
com.appsflyer.internal.AFi1vSDK;com_appsflyer_internal_AFi1vSDK_android_net_ConnectivityManager_getNetworkInfo(Landroid/net/ConnectivityManager; I Ljava/lang/String;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo com_appsflyer_internal_AFi1vSDK_android_net_ConnectivityManager_getNetworkInfo(android.net.ConnectivityManager p17, int p18, String p19)
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
com.appsflyer.internal.AFi1vSDK;valueOf()Ljava/lang/String;
*/

    public final String valueOf()
    {
        android.net.ConnectivityManager v6 = this.AFInAppEventType;
        if (v6 != null) {
            if (!com.appsflyer.internal.AFi1xSDK.AFInAppEventParameterName(com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_android_net_ConnectivityManager_getNetworkInfo(v6, 1, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsfuleyw=="))) {
                if (!com.appsflyer.internal.AFi1xSDK.AFInAppEventParameterName(com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_android_net_ConnectivityManager_getNetworkInfo(v6, 0, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsfuleyw=="))) {
                    int v0_3 = com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_com_ss_android_ugc_aweme_performance_lancet_IPCConnectivityManagerLancet_getActiveNetworkInfo(v6);
                    if (v0_3 != 0) {
                        int v0_4 = com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_android_net_NetworkInfo_getType(v0_3, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsfuleyw==");
                        if (v0_4 == 0) {
                            return "MOBILE";
                        } else {
                            if (v0_4 == 1) {
                                return "WIFI";
                            } else {
                                return "unknown";
                            }
                        }
                    }
                } else {
                    return "MOBILE";
                }
            } else {
                return "WIFI";
            }
        }
        return "unknown";
    }


}