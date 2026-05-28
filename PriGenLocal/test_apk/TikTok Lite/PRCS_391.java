/*Application Package Name: com.tiktok.lite.go
class PRCS_391 {
/**
com.appsflyer.internal.AFi1ySDK;com_appsflyer_internal_AFi1ySDK_android_net_ConnectivityManager_getAllNetworks(Landroid/net/ConnectivityManager; Ljava/lang/String;)[Landroid/net/Network;
*/

    public static android.net.Network[] com_appsflyer_internal_AFi1ySDK_android_net_ConnectivityManager_getAllNetworks(android.net.ConnectivityManager p18, String p19)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v9 = new Object[0];
        com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()[Landroid/net/Network;", p19);
        com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(208, "android/net/ConnectivityManager", "getAllNetworks", p18, v9, "android.net.Network[]", v10_1);
        if (!v1_0.intercept) {
            android.net.Network[] v4_0 = p18.getAllNetworks();
            v3_1.postInvoke(v4_0, 208, "android/net/ConnectivityManager", "getAllNetworks", p18, v9, v10_1, 1);
            return v4_0;
        } else {
            v3_1.postInvoke(0, 208, "android/net/ConnectivityManager", "getAllNetworks", p18, v9, v10_1, 0);
            return ((android.net.Network[]) v1_0.returnValue);
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