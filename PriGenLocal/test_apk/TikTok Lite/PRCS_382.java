/*Application Package Name: com.tiktok.lite.go
class PRCS_382 {
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
com.appsflyer.internal.AFi1uSDK;values()Z
*/

    public final boolean values()
    {
        android.net.Network v2 = this.AFKeystoreWrapper;
        if ((v2 != null) && (!kotlin.jvm.internal.Intrinsics.L(this.valueOf, "NetworkLost"))) {
            android.net.ConnectivityManager v1_1 = this.AFInAppEventType;
            if (v1_1 != null) {
                boolean v0_0 = com.appsflyer.internal.AFi1uSDK.com_appsflyer_internal_AFi1uSDK_android_net_ConnectivityManager_getNetworkCapabilities(v1_1, v2, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsfeleyw==");
                if (v0_0) {
                    return com.appsflyer.internal.AFi1uSDK.AFKeystoreWrapper(v0_0);
                }
            }
        }
        return 0;
    }


}