/*Application Package Name: com.tiktok.lite.go
class PRCS_339 {
/**
com.ss.mediakit.net.AVMDLMultiNetwork;com_ss_mediakit_net_AVMDLMultiNetwork_android_net_ConnectivityManager_registerNetworkCallback(Landroid/net/ConnectivityManager; Landroid/net/NetworkRequest; Landroid/net/ConnectivityManager$NetworkCallback; Ljava/lang/String;)V
*/

    public static void com_ss_mediakit_net_AVMDLMultiNetwork_android_net_ConnectivityManager_registerNetworkCallback(android.net.ConnectivityManager p17, android.net.NetworkRequest p18, android.net.ConnectivityManager$NetworkCallback p19, String p20)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v11 = new Object[2];
        v11[0] = p18;
        v11[1] = p19;
        com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/NetworkRequest;Landroid/net/ConnectivityManager$NetworkCallback;)V", p20);
        if (!v5_1.preInvoke(85, "android/net/ConnectivityManager", "registerNetworkCallback", p17, v11, "void", v12_1).intercept) {
            p17.registerNetworkCallback(p18, p19);
            v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", p17, v11, v12_1, 1);
            return;
        } else {
            v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", p17, v11, v12_1, 0);
            return;
        }
    }

/**
com.ss.mediakit.net.AVMDLMultiNetwork;registerNetworkChangeCallback(Landroid/content/Context;)Z
*/

    public static boolean registerNetworkChangeCallback(android.content.Context p5)
    {
        com.ss.mediakit.net.AVMDLMultiNetwork.initHandler(p5);
        if (com.ss.mediakit.net.AVMDLMultiNetwork.mCm != null) {
            android.net.NetworkRequest v4 = new android.net.NetworkRequest$Builder().build();
            try {
                if (com.ss.mediakit.medialoader.AVMDLDataLoader.getInstance().getConfig().mEnableNetworkChangeNotify == 1) {
                    com.ss.mediakit.net.AVMDLMultiNetwork.com_ss_mediakit_net_AVMDLMultiNetwork_android_net_ConnectivityManager_registerNetworkCallback(com.ss.mediakit.net.AVMDLMultiNetwork.mCm, v4, new com.ss.mediakit.net.AVMDLMultiNetwork$2(), "dzBzEhEpEcfZUV4gThuQKJLVr0WKQK1kAWEP+tNBHpIWOw83pg==");
                }
            } catch (String v0_4) {
                v0_4.printStackTrace();
                return 0;
            }
            return 1;
        } else {
            return 0;
        }
    }

/**
com.ss.mediakit.medialoader.AVMDLDataLoader;startInternal()V
*/

    public final void startInternal()
    {
        this.mWriteLock.lock();
        try {
            if (this.mState != 1) {
                this.initLogThread(this);
                if (this.mHandle != 0) {
                    this.tryLoadP2pPluginInternal();
                    this.setConfigureInternal(this.mConfigure);
                    if (com.ss.mediakit.medialoader.AVMDLDataLoader._start(this.mHandle) >= 0) {
                        this.mState = 1;
                    }
                }
            }
        } catch (int v1_0) {
            this.mWriteLock.unlock();
            throw v1_0;
        }
        this.mWriteLock.unlock();
        if (this.mConfigure.mEnableBenchMarkIOSpeed > 0) {
            int v4 = this.testFileIOSpeed();
            Object[] v2 = new Object[1];
            v2[0] = Integer.valueOf(v4);
            String.format(java.util.Locale.US, "test io average speed:%d", v2);
            if (v4 > 0) {
                this.setIntValue(1508, v4);
            }
        }
        android.content.Context v0_12 = this.mStartCompleteListener;
        if (v0_12 != null) {
            v0_12.onStartComplete();
        }
        if ((this.mState == 1) && (this.mConfigure.mEnableCellularUp > 0)) {
            com.ss.mediakit.net.AVMDLMultiNetwork.alwayUpCellular(com.ss.mediakit.medialoader.AVMDLDataLoader.getApplicationContext());
        }
        com.ss.mediakit.net.AVMDLMultiNetwork.registerNetworkChangeCallback(com.ss.mediakit.medialoader.AVMDLDataLoader.getApplicationContext());
        return;
    }


}