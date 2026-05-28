/*Application Package Name: org.fdroid.fdroid
class PRCS_21 {
/**
org.fdroid.fdroid.nearby.BonjourManager;isVpnActive(Landroid/content/Context;)Z
*/

    public static boolean isVpnActive(android.content.Context p1)
    {
        boolean v1_4 = ((android.net.ConnectivityManager) p1.getSystemService("connectivity"));
        boolean v1_5 = v1_4.getNetworkCapabilities(v1_4.getActiveNetwork());
        if (v1_5) {
            return v1_5.hasTransport(4);
        } else {
            return 0;
        }
    }

/**
org.fdroid.fdroid.nearby.BonjourManager;setVisible(Landroid/content/Context; Z)V
*/

    public static void setVisible(android.content.Context p1, boolean p2)
    {
        org.fdroid.fdroid.nearby.BonjourManager.context = new ref.WeakReference(p1);
        if ((org.fdroid.fdroid.nearby.BonjourManager.handler != null) && ((org.fdroid.fdroid.nearby.BonjourManager.handlerThread != null) && (org.fdroid.fdroid.nearby.BonjourManager.handlerThread.isAlive()))) {
            if (!org.fdroid.fdroid.nearby.BonjourManager.isVpnActive(p1)) {
                if (p2 == 0) {
                    org.fdroid.fdroid.nearby.BonjourManager.handler.sendEmptyMessage(144151873);
                } else {
                    org.fdroid.fdroid.nearby.BonjourManager.handler.sendEmptyMessage(4151873);
                }
            } else {
                org.fdroid.fdroid.nearby.BonjourManager.handler.sendEmptyMessage(72346752);
            }
            return;
        } else {
            android.util.Log.e("BonjourManager", "handlerThread is stopped, not changing visibility!");
            return;
        }
    }

/**
org.fdroid.fdroid.nearby.SwapService;onCreate()V
*/

    public void onCreate()
    {
        super.onCreate();
        int v1 = 1;
        this.startForeground(1, this.createNotification());
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager = androidx.localbroadcastmanager.content.LocalBroadcastManager.getInstance(this);
        org.fdroid.fdroid.nearby.SwapService.swapPreferences = this.getSharedPreferences("swap-state", 0);
        org.fdroid.fdroid.nearby.LocalHTTPDManager.start(this);
        android.net.wifi.WifiManager v0_3 = android.bluetooth.BluetoothAdapter.getDefaultAdapter();
        org.fdroid.fdroid.nearby.SwapService.bluetoothAdapter = v0_3;
        if (v0_3 != null) {
            org.fdroid.fdroid.nearby.SwapService.putBluetoothEnabledBeforeSwap(v0_3.isEnabled());
            if (org.fdroid.fdroid.nearby.SwapService.bluetoothAdapter.isEnabled()) {
                org.fdroid.fdroid.nearby.BluetoothManager.start(this);
            }
            this.registerReceiver(this.bluetoothScanModeChanged, new android.content.IntentFilter("android.bluetooth.adapter.action.SCAN_MODE_CHANGED"));
        }
        android.net.wifi.WifiManager v0_11 = ((android.net.wifi.WifiManager) androidx.core.content.ContextCompat.getSystemService(this.getApplicationContext(), android.net.wifi.WifiManager));
        org.fdroid.fdroid.nearby.SwapService.wifiManager = v0_11;
        if (v0_11 != null) {
            org.fdroid.fdroid.nearby.SwapService.putWifiEnabledBeforeSwap(v0_11.isWifiEnabled());
        }
        this.appsToSwap.addAll(org.fdroid.fdroid.nearby.SwapService.deserializePackages(org.fdroid.fdroid.nearby.SwapService.swapPreferences.getString("appsToSwap", "")));
        org.fdroid.fdroid.Preferences.get().registerLocalRepoHttpsListeners(this.httpsEnabledListener);
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.registerReceiver(this.onWifiChange, new android.content.IntentFilter("org.fdroid.fdroid.action.WIFI_CHANGE"));
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.registerReceiver(this.bluetoothPeerFound, new android.content.IntentFilter("BluetoothNewPeer"));
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.registerReceiver(this.bonjourPeerFound, new android.content.IntentFilter("BonjourNewPeer"));
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.registerReceiver(this.bonjourPeerRemoved, new android.content.IntentFilter("BonjourPeerRemoved"));
        if (android.os.Build$VERSION.SDK_INT <= 28) {
            if (!org.fdroid.fdroid.nearby.SwapService.getHotspotActivatedUserPreference()) {
                if (org.fdroid.fdroid.nearby.SwapService.getWifiVisibleUserPreference()) {
                    android.net.wifi.WifiManager v0_24 = org.fdroid.fdroid.nearby.SwapService.wifiManager;
                    if ((v0_24 != null) && (!v0_24.isWifiEnabled())) {
                        org.fdroid.fdroid.nearby.SwapService.wifiManager.setWifiEnabled(1);
                    }
                }
            } else {
                android.net.wifi.WifiManager v0_27 = cc.mvdan.accesspoint.WifiApControl.getInstance(this);
                if (v0_27 != null) {
                    v0_27.enable();
                }
            }
        }
        org.fdroid.fdroid.nearby.BonjourManager.start(this);
        if ((!org.fdroid.fdroid.nearby.SwapService.getWifiVisibleUserPreference()) && (!org.fdroid.fdroid.nearby.SwapService.getHotspotActivatedUserPreference())) {
            v1 = 0;
        }
        org.fdroid.fdroid.nearby.BonjourManager.setVisible(this, v1);
        return;
    }


}