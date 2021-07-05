package egov.mailbot.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import egov.mailbot.config.MainConfiguration;
import egov.mailbot.models.user.UserDetailResponse;
import egov.mailbot.models.user.UserSearchRequest;
import egov.mailbot.repository.ServiceRequestRepository;
import lombok.extern.slf4j.Slf4j;
import org.egov.common.contract.request.RequestInfo;
import org.egov.common.contract.request.Role;
import org.egov.common.contract.request.User;
import org.egov.tracer.model.CustomException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;


@Slf4j
@Service
public class UserService {


    private ObjectMapper mapper;
    private ServiceRequestRepository serviceRequestRepository;
    private MainConfiguration config;


    @Autowired
    public UserService(ObjectMapper mapper, ServiceRequestRepository serviceRequestRepository, MainConfiguration configuration) {
        this.mapper = mapper;
        this.serviceRequestRepository = serviceRequestRepository;
        this.config = configuration;
    }

    @Cacheable(value = "userToEmailMap", sync = true)
    public Map<String, User> getUsers(List<String> roleCodes, Set<String> tenantIds){
        Map<String, User> emailToUserMap = new HashMap<>();

        for(String tenant : tenantIds) {
            UserSearchRequest userSearchRequest = new UserSearchRequest();
            userSearchRequest.setRoleCodes(roleCodes);
            userSearchRequest.setTenantId(tenant);
            userSearchRequest.setUserType("EMPLOYEE");
            userSearchRequest.setActive(false);

            StringBuilder uri = new StringBuilder(config.getUserHost()).append(config.getUserSearchEndpoint());
            UserDetailResponse response = userCall(userSearchRequest, uri);

            if(response.getUser() != null){
                for(User user : response.getUser()){
                    if(user.getEmailId() == null)
                        continue;
                    String email = user.getEmailId().toLowerCase();
                    if(emailToUserMap.containsKey(email)) {
                        log.error("Multiple users exist for the same employee! Skipping employee email: "+emailToUserMap.get(email));
                        emailToUserMap.put(email, null);
                    } else{
                        String roleTenantId = null;
                        boolean isValid = true;
                        for (Role role : user.getRoles()) {
                            if(roleTenantId != null) {
                                if ( ! role.getTenantId().equalsIgnoreCase(roleTenantId)){
                                    log.warn("Skipping user, cross tenant role access: "+user.getEmailId());
                                    isValid = false;
                                    break;
                                }
                            }
                            roleTenantId = role.getTenantId();
                        }
                        if(isValid)
                            emailToUserMap.put(email, user);
                    }
                }
            }
        }

        //Expunge employees having multiple registrations across tenants with same email
        emailToUserMap.values().removeIf(Objects::isNull);
        return emailToUserMap;
    }

    private Set<String> getMobileNumbers(List<User> owners, RequestInfo requestInfo, String tenantId) {
        Set<String> listOfMobileNumbers = new HashSet<>();
        owners.forEach(owner -> {
            listOfMobileNumbers.add(owner.getMobileNumber());
        });
        StringBuilder uri = new StringBuilder(config.getUserHost()).append(config.getUserSearchEndpoint());
        UserSearchRequest userSearchRequest = new UserSearchRequest();
        userSearchRequest.setRequestInfo(requestInfo);
        userSearchRequest.setTenantId(tenantId);
        userSearchRequest.setUserType("CITIZEN");
        Set<String> availableMobileNumbers = new HashSet<>();

        listOfMobileNumbers.forEach(mobilenumber -> {
            userSearchRequest.setMobileNumber(mobilenumber);
            UserDetailResponse userDetailResponse = userCall(userSearchRequest, uri);
            if (CollectionUtils.isEmpty(userDetailResponse.getUser()))
                availableMobileNumbers.add(mobilenumber);
        });
        return availableMobileNumbers;
    }


    /**
     * Creates citizen role
     *
     * @return Role object for citizen
     */
    private Role getCitizenRole() {
        Role role = new Role();
        role.setCode("CITIZEN");
        role.setName("Citizen");
        return role;
    }


    /**
     * Returns UserDetailResponse by calling user service with given uri and object
     *
     * @param userRequest Request object for user service
     * @param uri         The address of the endpoint
     * @return Response from user service as parsed as userDetailResponse
     */
    private UserDetailResponse userCall(Object userRequest, StringBuilder uri) {
        String dobFormat = null;
        if (uri.toString().contains(config.getUserSearchEndpoint()) )
            dobFormat = "yyyy-MM-dd";
        try {
            LinkedHashMap responseMap = (LinkedHashMap) serviceRequestRepository.fetchResult(uri.toString(), userRequest);
            parseResponse(responseMap, dobFormat);
            UserDetailResponse userDetailResponse = mapper.convertValue(responseMap, UserDetailResponse.class);
            return userDetailResponse;
        } catch (IllegalArgumentException e) {
            throw new CustomException("IllegalArgumentException", "ObjectMapper not able to convertValue in userCall");
        }
    }


    /**
     * Parses date formats to long for all users in responseMap
     *
     * @param responeMap LinkedHashMap got from user api response
     */
    private void parseResponse(LinkedHashMap responeMap, String dobFormat) {
        List<LinkedHashMap> users = (List<LinkedHashMap>) responeMap.get("user");
        String format1 = "dd-MM-yyyy HH:mm:ss";
        if (users != null) {
            users.forEach(map -> {
                        map.put("createdDate", dateTolong((String) map.get("createdDate"), format1));
                        if ((String) map.get("lastModifiedDate") != null)
                            map.put("lastModifiedDate", dateTolong((String) map.get("lastModifiedDate"), format1));
                        if ((String) map.get("dob") != null)
                            map.put("dob", dateTolong((String) map.get("dob"), dobFormat));
                        if ((String) map.get("pwdExpiryDate") != null)
                            map.put("pwdExpiryDate", dateTolong((String) map.get("pwdExpiryDate"), format1));
                    }
            );
        }
    }

    /**
     * Converts date to long
     *
     * @param date   date to be parsed
     * @param format Format of the date
     * @return Long value of date
     */
    private Long dateTolong(String date, String format) {
        SimpleDateFormat f = new SimpleDateFormat(format);
        Date d = null;
        try {
            d = f.parse(date);
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return d.getTime();
    }


    /**
     * Call search in user service based on ownerids from criteria
     *
     * @param userSearchRequest    The search criteria
     * @param requestInfo The requestInfo of the request
     * @return Search response from user service based on ownerIds
     */
    public UserDetailResponse getUser(UserSearchRequest userSearchRequest, RequestInfo requestInfo) {
        StringBuilder uri = new StringBuilder(config.getUserHost()).append(config.getUserSearchEndpoint());
        UserDetailResponse userDetailResponse = userCall(userSearchRequest, uri);
        return userDetailResponse;
    }


    private UserDetailResponse searchByUserName(String userName, String tenantId) {
        UserSearchRequest userSearchRequest = new UserSearchRequest();
        userSearchRequest.setUserType("CITIZEN");
        userSearchRequest.setUserName(userName);
        userSearchRequest.setTenantId(config.getRootTenantId());
        StringBuilder uri = new StringBuilder(config.getUserHost()).append(config.getUserSearchEndpoint());
        return userCall(userSearchRequest, uri);

    }


    private UserDetailResponse isUserUpdatable(User owner, RequestInfo requestInfo) {
        UserSearchRequest userSearchRequest = new UserSearchRequest();
        userSearchRequest.setTenantId(config.getRootTenantId());
        userSearchRequest.setMobileNumber(owner.getMobileNumber());
        userSearchRequest.setUuid(Collections.singletonList(owner.getUuid()));
        userSearchRequest.setRequestInfo(requestInfo);
        userSearchRequest.setActive(false);
        userSearchRequest.setUserType(owner.getType());
        StringBuilder uri = new StringBuilder(config.getUserHost()).append(config.getUserSearchEndpoint());
        return userCall(userSearchRequest, uri);
    }


}
