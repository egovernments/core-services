package egov.mailbot;

import org.cache2k.extra.spring.SpringCache2kCacheManager;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Profile;

import java.util.concurrent.TimeUnit;

@SpringBootApplication
@ComponentScan(basePackages = { "egov", "egov.mailbot" , "egov.mailbot.config"})
@EnableCaching
public class Main {

    @Value("${cache.expiry.user.email.minutes}")
    private int userToEmailMapExpiry;

        public static void main(String[] args) throws Exception {
            SpringApplication.run(Main.class, args);
        }

    @Bean
    @Profile("!test")
    public CacheManager cacheManager() {
        return new SpringCache2kCacheManager()
                .addCaches(b->b.name("userToEmailMap").expireAfterWrite(userToEmailMapExpiry, TimeUnit.MINUTES).entryCapacity(10));
    }
}
