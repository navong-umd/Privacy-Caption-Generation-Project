/*Application Package Name: com.tiktok.lite.go
class PRCS_390 {
/**
com.ss.mediakit.net.AVMDLMultiNetwork;com_ss_mediakit_net_AVMDLMultiNetwork_android_net_ConnectivityManager_getNetworkInfo(Landroid/net/ConnectivityManager; Landroid/net/Network; Ljava/lang/String;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo com_ss_mediakit_net_AVMDLMultiNetwork_android_net_ConnectivityManager_getNetworkInfo(android.net.ConnectivityManager p17, android.net.Network p18, String p19)
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
com.ss.mediakit.net.AVMDLMultiNetwork;onAvailableInternal(Landroid/net/Network;)V
*/

    public static void onAvailableInternal(android.net.Network p4)
    {
        if (p4 != null) {
            com.ss.mediakit.medialoader.AVMDLDataLoader v0_0 = com.ss.mediakit.net.AVMDLMultiNetwork.mCm;
            if (v0_0 != null) {
                android.net.NetworkCapabilities v1_1 = com.ss.mediakit.net.AVMDLMultiNetwork.com_ss_mediakit_net_AVMDLMultiNetwork_android_net_ConnectivityManager_getNetworkInfo(v0_0, p4, "dzBzEhEpEcfZUV4gThuQKJLVr0WKQK1kAWEP+tNBHpIWOw83pg==");
                if (v1_1 != null) {
                    com.ss.mediakit.medialoader.AVMDLDataLoader v2_2 = new StringBuilder("network name: ");
                    v2_2.append(com.ss.mediakit.net.AVMDLMultiNetwork.com_ss_mediakit_net_AVMDLMultiNetwork_android_net_NetworkInfo_getTypeName(v1_1, "dzBzEhEpEcfZUV4gThuQKJLVr0WKQK1kAWEP+tNBHpIWOw83pg=="));
                    v2_2.append("[");
                    v2_2.append(com.ss.mediakit.net.AVMDLMultiNetwork.com_ss_mediakit_net_AVMDLMultiNetwork_android_net_NetworkInfo_getSubtypeName(v1_1, "dzBzEhEpEcfZUV4gThuQKJLVr0WKQK1kAWEP+tNBHpIWOw83pg=="));
                    v2_2.append("], state: ");
                    v2_2.append(v1_1.getDetailedState());
                    v2_2.append(" netid:");
                    v2_2.append(com.ss.mediakit.net.AVMDLMultiNetwork.getNetId(p4));
                    v2_2.toString();
                }
                android.net.NetworkCapabilities v1_0 = com.ss.mediakit.net.AVMDLMultiNetwork.com_ss_mediakit_net_AVMDLMultiNetwork_android_net_ConnectivityManager_getNetworkCapabilities(com.ss.mediakit.net.AVMDLMultiNetwork.mCm, p4, "dzBzEhEpEcfZUV4gThuQKJLVr0WKQK1kAWEP+tNBHpIWOw83pg==");
                if ((v1_0 == null) || ((!v1_0.hasTransport(0)) || (!v1_0.hasCapability(12)))) {
                    com.ss.mediakit.medialoader.AVMDLDataLoader.getInstance().onCellularAlwaysUp(0);
                    return;
                } else {
                    com.ss.mediakit.net.AVMDLMultiNetwork.onCellularNetwork(p4);
                    com.ss.mediakit.medialoader.AVMDLDataLoader.getInstance().onInitMultiNetworkEnv();
                }
            }
        }
        return;
    }

/**
com.ss.mediakit.net.AVMDLMultiNetwork;handleMessage(Landroid/os/Message;)V
*/

    public final void handleMessage(android.os.Message p8)
    {
        int v6_0;
        if (p8.obj == null) {
            v6_0 = 0;
        } else {
            v6_0 = ((android.net.Network) p8.obj);
        }
        Object[] v1_1 = new Object[2];
        v1_1[0] = Integer.valueOf(p8.what);
        v1_1[1] = v6_0;
        String.format(java.util.Locale.US, "----receive msg what:%d info:%s", v1_1);
        String v0_3 = p8.what;
        if (v0_3 == null) {
            com.ss.mediakit.net.AVMDLMultiNetwork.onAvailableInternal(v6_0);
        } else {
            if (v0_3 == 1) {
                com.ss.mediakit.net.AVMDLMultiNetwork.switchToCellularNetworkInternal();
            } else {
                if (v0_3 == 2) {
                    com.ss.mediakit.net.AVMDLMultiNetwork.switchToDefaultNetworkInternal();
                }
            }
        }
        Object[] v1_0 = new Object[2];
        v1_0[0] = Integer.valueOf(p8.what);
        v1_0[1] = v6_0;
        String.format(java.util.Locale.US, "****end proc msg what:%d info:%s", v1_0);
        return;
    }


}