/*Application Package Name: com.tiktok.lite.go
class PRCS_380 {
/**
com.appsflyer.internal.AFi1ySDK;com_appsflyer_internal_AFi1ySDK_android_net_ConnectivityManager_getNetworkCapabilities(Landroid/net/ConnectivityManager; Landroid/net/Network; Ljava/lang/String;)Landroid/net/NetworkCapabilities;
*/

    public static android.net.NetworkCapabilities com_appsflyer_internal_AFi1ySDK_android_net_ConnectivityManager_getNetworkCapabilities(android.net.ConnectivityManager p17, android.net.Network p18, String p19)
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
com.appsflyer.internal.AFi1ySDK;values()Z
*/

    public final boolean values()
    {
        int v6 = 0;
        try {
            boolean v0_3 = this.AFInAppEventType;
        } catch (Exception) {
            return v6;
        }
        if (!v0_3) {
            return v6;
        } else {
            android.net.Network[] v5 = com.appsflyer.internal.AFi1ySDK.com_appsflyer_internal_AFi1ySDK_android_net_ConnectivityManager_getAllNetworks(v0_3, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsceleyw==");
            if (v5 == null) {
                return v6;
            } else {
                java.util.List v4_2 = new java.util.ArrayList();
                int v3 = v5.length;
                int v2 = 0;
                while (v2 < v3) {
                    boolean v0_9 = com.appsflyer.internal.AFi1ySDK.com_appsflyer_internal_AFi1ySDK_android_net_ConnectivityManager_getNetworkCapabilities(this.AFInAppEventType, v5[v2], "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsceleyw==");
                    if (v0_9) {
                        v4_2.add(v0_9);
                    }
                    v2++;
                }
                java.util.List v4_0 = ((java.util.List) v4_2);
                if (((java.util.Collection) v4_0).isEmpty()) {
                    return v6;
                } else {
                    java.util.Iterator v1_0 = v4_0.iterator();
                    while (v1_0.hasNext()) {
                        if (com.appsflyer.internal.AFi1ySDK.AFInAppEventParameterName(((android.net.NetworkCapabilities) v1_0.next()))) {
                            v6 = 1;
                            break;
                        }
                    }
                    return v6;
                }
            }
        }
    }


}