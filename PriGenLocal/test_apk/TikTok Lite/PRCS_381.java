/*Application Package Name: com.tiktok.lite.go
class PRCS_381 {
/**
com.appsflyer.internal.AFi1uSDK;com_appsflyer_internal_AFi1uSDK_android_net_ConnectivityManager_getNetworkCapabilities(Landroid/net/ConnectivityManager; Landroid/net/Network; Ljava/lang/String;)Landroid/net/NetworkCapabilities;
*/

    public static android.net.NetworkCapabilities com_appsflyer_internal_AFi1uSDK_android_net_ConnectivityManager_getNetworkCapabilities(android.net.ConnectivityManager p17, android.net.Network p18, String p19)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v10 = new Object[1];
        v10[0] = p18;
        com.bytedance.helios.statichook.api.ExtraInfo v11_0 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/Network;)Landroid/net/NetworkCapabilities;", p19);
        com.bytedance.helios.statichook.api.Result v1_0 = v4_1.preInvoke(225, "android/net/ConnectivityManager", "getNetworkCapabilities", p17, v10, "android.net.NetworkCapabilities", v11_0);
        if (!v1_0.intercept) {
            android.net.NetworkCapabilities v5_0 = p17.getNetworkCapabilities(p18);
            v4_1.postInvoke(v5_0, 225, "android/net/ConnectivityManager", "getNetworkCapabilities", p17, v10, v11_0, 1);
            return v5_0;
        } else {
            v4_1.postInvoke(0, 225, "android/net/ConnectivityManager", "getNetworkCapabilities", p17, v10, v11_0, 0);
            return ((android.net.NetworkCapabilities) v1_0.returnValue);
        }
    }

/**
com.appsflyer.internal.AFi1uSDK;valueOf()Ljava/lang/String;
*/

    public final String valueOf()
    {
        android.net.Network v3 = this.AFKeystoreWrapper;
        if (v3 != null) {
            android.net.NetworkCapabilities v1_0 = this.AFInAppEventType;
            if (v1_0 != null) {
                android.net.NetworkCapabilities v1_1 = com.appsflyer.internal.AFi1uSDK.com_appsflyer_internal_AFi1uSDK_android_net_ConnectivityManager_getNetworkCapabilities(v1_0, v3, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsfeleyw==");
                if (v1_1 != null) {
                    if (!v1_1.hasTransport(1)) {
                        if (v1_1.hasTransport(0)) {
                            return "MOBILE";
                        }
                    } else {
                        return "WIFI";
                    }
                }
            }
        }
        return "unknown";
    }


}