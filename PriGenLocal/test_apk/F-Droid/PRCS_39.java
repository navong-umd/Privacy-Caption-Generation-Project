/*Application Package Name: org.fdroid.fdroid
class PRCS_39 {
/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;checkIfNewRepoOnSameWifi(Lorg/fdroid/fdroid/nearby/NewRepoConfig;)V
*/

    private void checkIfNewRepoOnSameWifi(org.fdroid.fdroid.nearby.NewRepoConfig p5)
    {
        if (!android.text.TextUtils.isEmpty(p5.getBssid())) {
            int v0_3 = ((android.net.wifi.WifiManager) androidx.core.content.ContextCompat.getSystemService(this.getApplicationContext(), android.net.wifi.WifiManager)).getConnectionInfo().getBSSID();
            if (!android.text.TextUtils.isEmpty(v0_3)) {
                int v1_1 = java.util.Locale.ENGLISH;
                if (!v0_3.toLowerCase(v1_1).equals(android.net.Uri.decode(p5.getBssid()).toLowerCase(v1_1))) {
                    Object[] v2_2 = new Object[1];
                    v2_2[0] = p5.getSsid();
                    android.widget.Toast.makeText(this, this.getString(org.fdroid.fdroid.R$string.not_on_same_wifi, v2_2), 1).show();
                }
            } else {
                return;
            }
        }
        return;
    }

/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;checkIncomingIntent()V
*/

    private void checkIncomingIntent()
    {
        android.widget.Toast v0_0 = this.getIntent();
        if ("requestSwap".equals(v0_0.getAction())) {
            org.fdroid.fdroid.nearby.NewRepoConfig v1_4 = v0_0.getData();
            if ((v1_4 == null) || ((org.fdroid.fdroid.nearby.SwapWorkflowActivity.isSwapUrl(v1_4)) || (org.fdroid.fdroid.net.BluetoothDownloader.isBluetoothUri(v1_4)))) {
                org.fdroid.fdroid.nearby.NewRepoConfig v1_1 = new org.fdroid.fdroid.nearby.NewRepoConfig(this, v0_0);
                this.confirmSwapConfig = v1_1;
                this.checkIfNewRepoOnSameWifi(v1_1);
                return;
            } else {
                Object[] v3 = new Object[1];
                v3[0] = v1_4;
                android.widget.Toast.makeText(this, this.getString(org.fdroid.fdroid.R$string.swap_toast_invalid_url, v3), 1).show();
                return;
            }
        } else {
            return;
        }
    }

/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;onResume()V
*/

    protected void onResume()
    {
        super.onResume();
        this.localBroadcastManager.registerReceiver(this.onWifiStateChanged, new android.content.IntentFilter("org.fdroid.fdroid.action.WIFI_CHANGE"));
        this.localBroadcastManager.registerReceiver(this.localRepoStatus, new android.content.IntentFilter("localRepoStatusAction"));
        this.localBroadcastManager.registerReceiver(this.bonjourFound, new android.content.IntentFilter("BonjourNewPeer"));
        this.localBroadcastManager.registerReceiver(this.bonjourRemoved, new android.content.IntentFilter("BonjourPeerRemoved"));
        this.localBroadcastManager.registerReceiver(this.bonjourStatusReceiver, new android.content.IntentFilter("BonjourStatus"));
        this.localBroadcastManager.registerReceiver(this.bluetoothFound, new android.content.IntentFilter("BluetoothNewPeer"));
        this.localBroadcastManager.registerReceiver(this.bluetoothStatusReceiver, new android.content.IntentFilter("BluetoothStatus"));
        this.registerReceiver(this.bluetoothScanModeChanged, new android.content.IntentFilter("android.bluetooth.adapter.action.SCAN_MODE_CHANGED"));
        this.checkIncomingIntent();
        if ((this.service != null) && (this.newIntent)) {
            this.showRelevantView();
            this.newIntent = 0;
        }
        if (this.currentSwapViewLayoutRes == org.fdroid.fdroid.R$layout.swap_start_swap) {
            this.updateWifiBannerVisibility();
        }
        return;
    }


}