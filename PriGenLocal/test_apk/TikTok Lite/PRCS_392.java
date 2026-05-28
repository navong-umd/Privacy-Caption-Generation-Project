/*Application Package Name: com.tiktok.lite.go
class PRCS_392 {
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
com.appsflyer.internal.AFi1ySDK;valueOf()Ljava/lang/String;
*/

    public final String valueOf()
    {
        String v0_0 = this.AFInAppEventType;
        if (v0_0 != null) {
            String v0_11 = com.appsflyer.internal.AFi1ySDK.com_appsflyer_internal_AFi1ySDK_android_net_ConnectivityManager_getAllNetworks(v0_0, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsceleyw==");
            if (v0_11 != null) {
                int v1_3 = X.8Be.LFFLLL(v0_11);
                if (v1_3 != 0) {
                    String v0_3 = X.8F0.LCCII(v1_3, new com.appsflyer.internal.AFi1ySDK$3(this));
                    if (v0_3 != null) {
                        java.util.Iterator v2 = v0_3.L();
                        while (v2.hasNext()) {
                            int v1_0 = v2.next();
                            if (com.appsflyer.internal.AFi1xSDK.AFInAppEventParameterName(((android.net.NetworkInfo) v1_0))) {
                            }
                            int v1_1 = ((android.net.NetworkInfo) v1_0);
                            if (v1_1 != 0) {
                                int v1_2 = com.appsflyer.internal.AFi1ySDK.com_appsflyer_internal_AFi1ySDK_android_net_NetworkInfo_getType(v1_1, "dzBzEgMqT9naWU4kV1yNaEAr35CqUcZV5bxsceleyw==");
                                if (v1_2 == 0) {
                                    return "MOBILE";
                                } else {
                                    if (v1_2 == 1) {
                                        return "WIFI";
                                    } else {
                                        return "unknown";
                                    }
                                }
                            }
                        }
                        v1_0 = 0;
                    }
                }
            }
        }
        return "unknown";
    }


}