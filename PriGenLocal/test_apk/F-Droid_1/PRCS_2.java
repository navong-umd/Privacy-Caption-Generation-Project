/* Application Package Name: org.fdroid.fdroid */
class PRCS_2 {
/**
org.fdroid.fdroid.Preferences;setDefaultForDataOnlyConnection(Landroid/content/Context;)V
*/

    void setDefaultForDataOnlyConnection(android.content.Context p3)
    {
        android.content.SharedPreferences$Editor v3_7 = ((android.net.ConnectivityManager) androidx.core.content.ContextCompat.getSystemService(p3, android.net.ConnectivityManager));
        if (v3_7 != null) {
            String v0_4 = v3_7.getActiveNetworkInfo();
            if ((v0_4 != null) && ((v0_4.isConnectedOrConnecting()) && ((v0_4.getType() == 0) && (!v3_7.getNetworkInfo(1).isConnectedOrConnecting())))) {
                this.preferences.edit().putInt("overData", 2).apply();
            }
            return;
        } else {
            return;
        }
    }


}
