/*Application Package Name: com.tiktok.lite.go
class PRCS_20 {
/**
com.appsflyer.internal.AFi1vSDK;com_appsflyer_internal_AFi1vSDK_android_net_ConnectivityManager_getActiveNetworkInfo(Landroid/net/ConnectivityManager; Ljava/lang/String;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo com_appsflyer_internal_AFi1vSDK_android_net_ConnectivityManager_getActiveNetworkInfo(android.net.ConnectivityManager p18, String p19)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v9 = new Object[0];
        com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", p19);
        com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, "android.net.NetworkInfo", v10_1);
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
com.appsflyer.internal.AFi1vSDK;com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(android.net.ConnectivityManager p1)
    {
        try {
            return com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_android_net_ConnectivityManager_getActiveNetworkInfo(p1, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsfuleyw==");
        } catch (android.net.NetworkInfo v0_2) {
            v0_2.printStackTrace();
            return X.1Mw.L();
        }
    }

/**
com.appsflyer.internal.AFi1vSDK;com_appsflyer_internal_AFi1vSDK_com_ss_android_ugc_aweme_performance_lancet_IPCConnectivityManagerLancet_getActiveNetworkInfo(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo com_appsflyer_internal_AFi1vSDK_com_ss_android_ugc_aweme_performance_lancet_IPCConnectivityManagerLancet_getActiveNetworkInfo(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_20) {
            X.5If.L(v0_20);
            return com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(p3);
        }
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(p3);
                }
            } else {
                return com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(p3);
            }
        } else {
            return com.appsflyer.internal.AFi1vSDK.com_appsflyer_internal_AFi1vSDK_com_bytedance_otis_optimise_lancet_NetworkInfoManager_getActiveNetworkInfo(p3);
        }
    }


}