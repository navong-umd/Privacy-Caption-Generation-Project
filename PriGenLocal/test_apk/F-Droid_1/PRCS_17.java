/* Application Package Name: org.fdroid.fdroid */
class PRCS_17 {
/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;setupWifiAP()V
*/

    private void setupWifiAP()
    {
        String v0_0 = this.wifiApControl;
        if (v0_0 != null) {
            org.fdroid.fdroid.nearby.SwapService.putHotspotEnabledBeforeSwap(v0_0.isEnabled());
            if (android.os.Build$VERSION.SDK_INT <= 28) {
                this.wifiManager.setWifiEnabled(0);
            }
            try {
                if (!this.wifiApControl.enable()) {
                    android.widget.Toast.makeText(this, org.fdroid.fdroid.R$string.swap_toast_could_not_enable_hotspot, 1).show();
                    org.fdroid.fdroid.nearby.SwapService.putHotspotActivatedUserPreference(0);
                    android.util.Log.e("SwapWorkflowActivity", "Could not enable WiFi AP.");
                } else {
                    android.widget.Toast.makeText(this, org.fdroid.fdroid.R$string.swap_toast_hotspot_enabled, 0).show();
                    org.fdroid.fdroid.nearby.SwapService.putHotspotActivatedUserPreference(1);
                }
            } catch (String v0_4) {
                android.util.Log.e("SwapWorkflowActivity", "Error enabling WiFi: ", v0_4);
            }
            return;
        } else {
            android.util.Log.e("SwapWorkflowActivity", "WiFi AP is null");
            android.widget.Toast.makeText(this, org.fdroid.fdroid.R$string.swap_toast_could_not_enable_hotspot, 1).show();
            return;
        }
    }


}
