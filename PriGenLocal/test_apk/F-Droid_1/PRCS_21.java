/* Application Package Name: org.fdroid.fdroid */
class PRCS_21 {
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


}
