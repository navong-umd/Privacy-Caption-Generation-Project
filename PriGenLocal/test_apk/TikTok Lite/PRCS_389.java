/*Application Package Name: com.tiktok.lite.go
class PRCS_389 {
/**
com.appsflyer.internal.AFi1ySDK;com_appsflyer_internal_AFi1ySDK$3_android_net_ConnectivityManager_getNetworkInfo(Landroid/net/ConnectivityManager; Landroid/net/Network; Ljava/lang/String;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo com_appsflyer_internal_AFi1ySDK$3_android_net_ConnectivityManager_getNetworkInfo(android.net.ConnectivityManager p17, android.net.Network p18, String p19)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v10 = new Object[1];
        v10[0] = p18;
        com.bytedance.helios.statichook.api.ExtraInfo v11_0 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/Network;)Landroid/net/NetworkInfo;", p19);
        com.bytedance.helios.statichook.api.Result v1_0 = v4_1.preInvoke(195, "android/net/ConnectivityManager", "getNetworkInfo", p17, v10, "android.net.NetworkInfo", v11_0);
        if (!v1_0.intercept) {
            android.net.NetworkInfo v5_0 = p17.getNetworkInfo(p18);
            v4_1.postInvoke(v5_0, 195, "android/net/ConnectivityManager", "getNetworkInfo", p17, v10, v11_0, 1);
            return v5_0;
        } else {
            v4_1.postInvoke(0, 195, "android/net/ConnectivityManager", "getNetworkInfo", p17, v10, v11_0, 0);
            return ((android.net.NetworkInfo) v1_0.returnValue);
        }
    }

/**
com.appsflyer.internal.AFi1ySDK;values(Landroid/net/Network;)Landroid/net/NetworkInfo;
*/

    public final android.net.NetworkInfo values(android.net.Network p3)
    {
        return com.appsflyer.internal.AFi1ySDK$3.com_appsflyer_internal_AFi1ySDK$3_android_net_ConnectivityManager_getNetworkInfo(this.valueOf.AFInAppEventType, p3, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsceleyw==");
    }

/**
com.appsflyer.internal.AFi1ySDK;invoke(Ljava/lang/Object;)Ljava/lang/Object;
*/

    public final synthetic Object invoke(Object p2)
    {
        return this.values(((android.net.Network) p2));
    }


}