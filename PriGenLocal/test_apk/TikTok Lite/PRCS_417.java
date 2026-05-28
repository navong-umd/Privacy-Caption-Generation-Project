/*Application Package Name: com.tiktok.lite.go
class PRCS_417 {
/**
X.6dW;run()V
*/

    public final void run()
    {
        super.run();
        com.bytedance.helios.statichook.api.Result v4_1 = this.LB;
        try {
            if (v4_1 != null) {
                long v3_4 = v4_1.getPackageName();
                android.os.Bundle v1_0 = v4_1.getString(v4_1.getApplicationInfo().labelRes);
                if ((!android.text.TextUtils.isEmpty(v1_0)) && (!android.text.TextUtils.isEmpty(v3_4))) {
                    long v3_3;
                    android.accounts.Account v0_4 = new android.accounts.Account(v1_0, v3_4);
                    android.accounts.AccountManager v12_0 = android.accounts.AccountManager.get(v4_1);
                    com.bytedance.helios.statichook.api.HeliosApiHook v7_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                    Object[] v13_0 = new Object[3];
                    v13_0[0] = v0_4;
                    v13_0[1] = 0;
                    v13_0[2] = 0;
                    com.bytedance.helios.statichook.api.ExtraInfo v14_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/accounts/Account;Ljava/lang/String;Landroid/os/Bundle;)Z", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPq9cJeA3TFXudDTnScXVY6BemvVKwx1jBfsrg==");
                    com.bytedance.helios.statichook.api.Result v4_2 = v7_1.preInvoke(10005, "android/accounts/AccountManager", "addAccountExplicitly", v12_0, v13_0, "boolean", v14_1);
                    if (!v4_2.intercept) {
                        v3_3 = v12_0.addAccountExplicitly(v0_4, 0, 0);
                        v7_1.postInvoke(Boolean.valueOf(v3_3), 10005, "android/accounts/AccountManager", "addAccountExplicitly", v12_0, v13_0, v14_1, 1);
                    } else {
                        v7_1.postInvoke(0, 10005, "android/accounts/AccountManager", "addAccountExplicitly", v12_0, v13_0, v14_1, 0);
                        v3_3 = ((Boolean) v4_2.returnValue).booleanValue();
                    }
                    if (v3_3 != 0) {
                        android.content.ContentResolver.setIsSyncable(v0_4, "com.ss.android.account.AccountProvider1340", 1);
                        android.content.ContentResolver.setSyncAutomatically(v0_4, "com.ss.android.account.AccountProvider1340", 1);
                        android.content.ContentResolver.addPeriodicSync(v0_4, "com.ss.android.account.AccountProvider1340", new android.os.Bundle(), 1200);
                    }
                }
            }
        } catch (Throwable) {
        }
        return;
    }


}